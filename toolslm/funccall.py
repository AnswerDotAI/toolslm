# AUTOGENERATED! DO NOT EDIT! File to edit: ../01_funccall.ipynb.

# %% auto 0
__all__ = ['empty', 'get_schema', 'python']

# %% ../01_funccall.ipynb 2
import inspect
from fastcore.utils import *
from fastcore.docments import docments

# %% ../01_funccall.ipynb 3
empty = inspect.Parameter.empty

# %% ../01_funccall.ipynb 11
def _types(t:type)->tuple[str,Optional[str]]:
    "Tuple of json schema type name and (if appropriate) array item name."
    if t is empty: raise TypeError('Missing type')
    tmap = {int:"integer", float:"number", str:"string", bool:"boolean", list:"array", dict:"object"}
    tmap.update({k.__name__: v for k, v in tmap.items()})
    if getattr(t, '__origin__', None) in (list,tuple): return "array", tmap.get(t.__args__[0].__name__, "object")
    elif isinstance(t, str): return tmap.get(t, "object"), None
    else: return tmap.get(t.__name__, "object"), None

# %% ../01_funccall.ipynb 16
def _param(name, info):
    "json schema parameter given `name` and `info` from docments full dict."
    paramt,itemt = _types(info.anno)
    pschema = dict(type=paramt, description=info.docment or "")
    if itemt: pschema["items"] = {"type": itemt}
    if info.default is not empty: pschema["default"] = info.default
    return pschema

# %% ../01_funccall.ipynb 19
def _get_nested_schema(obj):
    "Generate nested JSON schema for a class or function"
    d = docments(obj, full=True)
    props,req,defs = {},{},{}
    for n,o in d.items():
        if n == 'return': continue
        props[n] = p = _param(n,o)
        if o.default is empty: req[n] = True
        t = o.anno.__args__[0] if hasattr(o.anno, '__args__') else o.anno
        if isinstance(t, type) and not issubclass(t, (int, float, str, bool)):
            defs[t.__name__] = _get_nested_schema(t)
            p['items' if p['type']=='array' else '$ref'] = f'#/$defs/{t.__name__}'
    res = dict(type='object', properties=props)
    if isinstance(obj, type): res['title'] = obj.__name__
    if req: res['required'] = list(req)
    if defs: res['$defs'] = defs
    return res

# %% ../01_funccall.ipynb 20
def get_schema(f:callable, pname='input_schema')->dict:
    "Generate JSON schema for a class, function, or method"
    schema = _get_nested_schema(f)
    desc = f.__doc__
    assert desc, "Docstring missing!"
    d = docments(f, full=True)
    ret = d.pop('return')
    if ret.anno is not empty: desc += f'\n\nReturns:\n- type: {_types(ret.anno)[0]}'
    return dict(name=f.__name__, description=desc, pname=schema)

# %% ../01_funccall.ipynb 30
import ast, time, signal, traceback
from fastcore.utils import *

# %% ../01_funccall.ipynb 31
def _copy_loc(new, orig):
    "Copy location information from original node to new node and all children."
    new = ast.copy_location(new, orig)
    for field, o in ast.iter_fields(new):
        if isinstance(o, ast.AST): setattr(new, field, _copy_loc(o, orig))
        elif isinstance(o, list): setattr(new, field, [_copy_loc(value, orig) for value in o])
    return new

# %% ../01_funccall.ipynb 33
def _run(code:str ):
    "Run `code`, returning final expression (similar to IPython)"
    tree = ast.parse(code)
    last_node = tree.body[-1] if tree.body else None
    
    # If the last node is an expression, modify the AST to capture the result
    if isinstance(last_node, ast.Expr):
        tgt = [ast.Name(id='_result', ctx=ast.Store())]
        assign_node = ast.Assign(targets=tgt, value=last_node.value)
        tree.body[-1] = _copy_loc(assign_node, last_node)

    compiled_code = compile(tree, filename='<ast>', mode='exec')
    namespace = {}
    stdout_buffer = io.StringIO()
    saved_stdout = sys.stdout
    sys.stdout = stdout_buffer
    try: exec(compiled_code, namespace)
    finally: sys.stdout = saved_stdout
    _result = namespace.get('_result', None)
    if _result is not None: return _result
    return stdout_buffer.getvalue().strip()

# %% ../01_funccall.ipynb 38
def python(code, # Code to execute
           timeout=5 # Maximum run time in seconds before a `TimeoutError` is raised
          ): # Result of last node, if it's an expression, or `None` otherwise
    """Executes python `code` with `timeout` and returning final expression (similar to IPython).
    Raised exceptions are returned as a string, with a stack trace."""
    def handler(*args): raise TimeoutError()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try: return _run(code)
    except Exception as e: return traceback.format_exc()
    finally: signal.alarm(0)
