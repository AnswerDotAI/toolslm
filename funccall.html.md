# funccall source


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

<details open class="code-fold">
<summary>Exported source</summary>

``` python
import inspect
from collections import abc
from fastcore.utils import *
from fastcore.docments import docments
```

</details>

## Function calling

Many LLMs do function calling (aka tool use) by taking advantage of JSON
schema.

We’ll use [docments](https://fastcore.fast.ai/docments.html) to make
getting JSON schema from Python functions as ergonomic as possible. Each
parameter (and the return value) should have a type, and a docments
comment with the description of what it is. Here’s an example:

``` python
def silly_sum(
    a:int, # First thing to sum
    b:int=1, # Second thing to sum
    c:list[int]=None, # A pointless argument
) -> int: # The sum of the inputs
    "Adds a + b."
    return a + b
```

This is what `docments` makes of that:

``` python
d = docments(silly_sum, full=True)
d
```

``` json
{ 'a': { 'anno': <class 'int'>,
         'default': <class 'inspect._empty'>,
         'docment': 'First thing to sum'},
  'b': {'anno': <class 'int'>, 'default': 1, 'docment': 'Second thing to sum'},
  'c': {'anno': list[int], 'default': None, 'docment': 'A pointless argument'},
  'return': { 'anno': <class 'int'>,
              'default': <class 'inspect._empty'>,
              'docment': 'The sum of the inputs'}}
```

Note that this is an
[AttrDict](https://fastcore.fast.ai/basics.html#attrdict) so we can
treat it like an object, *or* a dict:

``` python
d.a.docment, d['a']['anno']
```

    ('First thing to sum', int)

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def _types(t:type)->tuple[str,Optional[str]]:
    "Tuple of json schema type name and (if appropriate) array item name."
    if t is empty: raise TypeError('Missing type')
    tmap = {int:"integer", float:"number", str:"string", bool:"boolean", list:"array", dict:"object"}
    tmap.update({k.__name__: v for k, v in tmap.items()})
    if getattr(t, '__origin__', None) in (list,tuple): return "array", tmap.get(t.__args__[0].__name__, "object")
    elif isinstance(t, str): return tmap.get(t, "object"), None
    else: return tmap.get(t.__name__, "object"), None
```

</details>

This internal function is needed to convert Python types into JSON
schema types.

``` python
_types(list[int]), _types(int), _types('int')
```

    (('array', 'integer'), ('integer', None), ('integer', None))

Will also convert custom types to the `object` type.

``` python
class Custom: a: int
_types(list[Custom]), _types(Custom)
```

    (('array', 'object'), ('object', None))

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def _param(name, info):
    "json schema parameter given `name` and `info` from docments full dict."
    paramt,itemt = _types(info.anno)
    pschema = dict(type=paramt, description=info.docment or "")
    if itemt: pschema["items"] = {"type": itemt}
    if info.default is not empty: pschema["default"] = info.default
    return pschema
```

</details>

This private function converts a key/value pair from the `docments`
structure into the `dict` that will be needed for the schema.

``` python
n,o = first(d.items())
print(n,'//', o)
_param(n, o)
```

    a // {'docment': 'First thing to sum', 'anno': <class 'int'>, 'default': <class 'inspect._empty'>}

    {'type': 'integer', 'description': 'First thing to sum'}

``` python
# Test primitive types
defs = {}
assert _handle_type(int, defs) == {'type': 'integer'}
assert _handle_type(str, defs) == {'type': 'string'}
assert _handle_type(bool, defs) == {'type': 'boolean'}
assert _handle_type(float, defs) == {'type': 'number'}

# Test custom class
class TestClass:
    def __init__(self, x: int, y: int): store_attr()

result = _handle_type(TestClass, defs)
assert result == {'$ref': '#/$defs/TestClass'}
assert 'TestClass' in defs
assert defs['TestClass']['type'] == 'object'
assert 'properties' in defs['TestClass']
```

``` python
# Test primitive types in containers
assert _handle_container(list, (int,), defs) == {'type': 'array', 'items': {'type': 'integer'}}
assert _handle_container(tuple, (str,), defs) == {'type': 'array', 'items': {'type': 'string'}}
assert _handle_container(set, (str,), defs) == {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}
assert _handle_container(dict, (str,bool), defs) == {'type': 'object', 'additionalProperties': {'type': 'boolean'}}

result = _handle_container(list, (TestClass,), defs)
assert result == {'type': 'array', 'items': {'$ref': '#/$defs/TestClass'}}
assert 'TestClass' in defs

# Test complex nested structure
ComplexType = dict[str, list[TestClass]]
result = _handle_container(dict, (str, list[TestClass]), defs)
assert result == {
    'type': 'object',
    'additionalProperties': {
        'type': 'array',
        'items': {'$ref': '#/$defs/TestClass'}
    }
}
```

``` python
# Test processing of a required integer property
props, req = {}, {}
class TestClass:
    "Test class"
    def __init__(
        self,
        x: int, # First thing
        y: list[float], # Second thing
        z: str = "default", # Third thing
    ): store_attr()

d = docments(TestClass, full=True)
_process_property('x', d.x, props, req, defs)
assert 'x' in props
assert props['x']['type'] == 'integer'
assert 'x' in req

# Test processing of a required list property
_process_property('y', d.y, props, req, defs)
assert 'y' in props
assert props['y']['type'] == 'array'
assert props['y']['items']['type'] == 'number'
assert 'y' in req

# Test processing of an optional string property with default
_process_property('z', d.z, props, req, defs)
assert 'z' in props
assert props['z']['type'] == 'string'
assert props['z']['default'] == "default"
assert 'z' not in req
```

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/funccall.py#L89"
target="_blank" style="float:right; font-size:smaller">source</a>

### get_schema

>  get_schema (f:<built-infunctioncallable>, pname='input_schema')

*Generate JSON schema for a class, function, or method*

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def get_schema(f:callable, pname='input_schema')->dict:
    "Generate JSON schema for a class, function, or method"
    schema = _get_nested_schema(f)
    desc = f.__doc__
    assert desc, "Docstring missing!"
    d = docments(f, full=True)
    ret = d.pop('return')
    if ret.anno is not empty: desc += f'\n\nReturns:\n- type: {_types(ret.anno)[0]}'
    return {"name": f.__name__, "description": desc, pname: schema}
```

</details>

Putting this all together, we can now test getting a schema from
`silly_sum`. The tool use spec doesn’t support return annotations
directly, so we put that in the description instead.

``` python
s = get_schema(silly_sum)
desc = s.pop('description')
print(desc)
s
```

    Adds a + b.

    Returns:
    - type: integer

    {'name': 'silly_sum',
     'input_schema': {'type': 'object',
      'properties': {'a': {'type': 'integer', 'description': 'First thing to sum'},
       'b': {'type': 'integer',
        'description': 'Second thing to sum',
        'default': 1},
       'c': {'type': 'array',
        'description': 'A pointless argument',
        'items': {'type': 'integer'},
        'default': None}},
      'title': None,
      'required': ['a']}}

This also works with string annotations, e.g:

``` python
def silly_test(
    a: 'int',  # quoted type hint
):
    "Mandatory docstring"
    return a

get_schema(silly_test)
```

    {'name': 'silly_test',
     'description': 'Mandatory docstring',
     'input_schema': {'type': 'object',
      'properties': {'a': {'type': 'integer', 'description': 'quoted type hint'}},
      'title': None,
      'required': ['a']}}

This also works with class methods:

``` python
class Dummy:
    def sums(
        self,
        a:int,  # First thing to sum
        b:int=1 # Second thing to sum
    ) -> int: # The sum of the inputs
        "Adds a + b."
        print(f"Finding the sum of {a} and {b}")
        return a + b

get_schema(Dummy.sums)
```

    {'name': 'sums',
     'description': 'Adds a + b.\n\nReturns:\n- type: integer',
     'input_schema': {'type': 'object',
      'properties': {'a': {'type': 'integer', 'description': 'First thing to sum'},
       'b': {'type': 'integer',
        'description': 'Second thing to sum',
        'default': 1}},
      'title': None,
      'required': ['a']}}

[`get_schema`](https://AnswerDotAI.github.io/toolslm/funccall.html#get_schema)
also handles more complicated structures such as nested classes. This is
useful for things like structured outputs.

``` python
class Turn:
    "Turn between two speakers"
    def __init__(
        self,
        speaker_a:str, # First speaker to speak's message
        speaker_b:str,  # Second speaker to speak's message
    ): store_attr()

class Conversation:
    "A conversation between two speakers"
    def __init__(
        self,
        turns:list[Turn], # Turns of the conversation
    ): store_attr()

get_schema(Conversation)
```

    {'name': 'Conversation',
     'description': 'A conversation between two speakers',
     'input_schema': {'type': 'object',
      'properties': {'turns': {'type': 'array',
        'description': 'Turns of the conversation',
        'items': {'$ref': '#/$defs/Turn'}}},
      'title': 'Conversation',
      'required': ['turns'],
      '$defs': {'Turn': {'type': 'object',
        'properties': {'speaker_a': {'type': 'string',
          'description': "First speaker to speak's message"},
         'speaker_b': {'type': 'string',
          'description': "Second speaker to speak's message"}},
        'title': 'Turn',
        'required': ['speaker_a', 'speaker_b']}}}}

``` python
class DictConversation:
    "A conversation between two speakers"
    def __init__(
        self,
        turns:dict[str,list[Turn]], # dictionary of topics and the Turns of the conversation
    ): store_attr()

get_schema(DictConversation)
```

    {'name': 'DictConversation',
     'description': 'A conversation between two speakers',
     'input_schema': {'type': 'object',
      'properties': {'turns': {'type': 'object',
        'description': 'dictionary of topics and the Turns of the conversation',
        'additionalProperties': {'type': 'array',
         'items': {'$ref': '#/$defs/Turn'}}}},
      'title': 'DictConversation',
      'required': ['turns'],
      '$defs': {'Turn': {'type': 'object',
        'properties': {'speaker_a': {'type': 'string',
          'description': "First speaker to speak's message"},
         'speaker_b': {'type': 'string',
          'description': "Second speaker to speak's message"}},
        'title': 'Turn',
        'required': ['speaker_a', 'speaker_b']}}}}

``` python
class SetConversation:
    "A conversation between two speakers"
    def __init__(
        self,
        turns:set[Turn], # the unique Turns of the conversation
    ): store_attr()

get_schema(SetConversation)
```

    {'name': 'SetConversation',
     'description': 'A conversation between two speakers',
     'input_schema': {'type': 'object',
      'properties': {'turns': {'type': 'array',
        'description': 'the unique Turns of the conversation',
        'items': {'$ref': '#/$defs/Turn'},
        'uniqueItems': True}},
      'title': 'SetConversation',
      'required': ['turns'],
      '$defs': {'Turn': {'type': 'object',
        'properties': {'speaker_a': {'type': 'string',
          'description': "First speaker to speak's message"},
         'speaker_b': {'type': 'string',
          'description': "Second speaker to speak's message"}},
        'title': 'Turn',
        'required': ['speaker_a', 'speaker_b']}}}}

### Python tool

In language model clients it’s often useful to have a ‘code interpreter’
– this is something that runs code, and generally outputs the result of
the last expression (i.e like IPython or Jupyter).

In this section we’ll create the
[`python`](https://AnswerDotAI.github.io/toolslm/funccall.html#python)
function, which executes a string as Python code, with an optional
timeout. If the last line is an expression, we’ll return that – just
like in IPython or Jupyter, but without needing them installed.

<details open class="code-fold">
<summary>Exported source</summary>

``` python
import ast, time, signal, traceback
from fastcore.utils import *
```

</details>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def _copy_loc(new, orig):
    "Copy location information from original node to new node and all children."
    new = ast.copy_location(new, orig)
    for field, o in ast.iter_fields(new):
        if isinstance(o, ast.AST): setattr(new, field, _copy_loc(o, orig))
        elif isinstance(o, list): setattr(new, field, [_copy_loc(value, orig) for value in o])
    return new
```

</details>

This is an internal function that’s needed for
[`_run`](https://AnswerDotAI.github.io/toolslm/funccall.html#_run) to
ensure that location information is available in the abstract syntax
tree (AST), since otherwise python complains.

<details open class="code-fold">
<summary>Exported source</summary>

``` python
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
```

</details>

This is the internal function used to actually run the code – we pull
off the last AST to see if it’s an expression (i.e something that
returns a value), and if so, we store it to a special `_result` variable
so we can return it.

``` python
_run('import math;math.factorial(12)')
```

    479001600

``` python
_run('print(1+1)')
```

    '2'

We now have the machinery needed to create our
[`python`](https://AnswerDotAI.github.io/toolslm/funccall.html#python)
function.

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/funccall.py#L136"
target="_blank" style="float:right; font-size:smaller">source</a>

### python

>  python (code, timeout=5)

*Executes python `code` with `timeout` and returning final expression
(similar to IPython). Raised exceptions are returned as a string, with a
stack trace.*

<table>
<colgroup>
<col style="width: 6%" />
<col style="width: 25%" />
<col style="width: 34%" />
<col style="width: 34%" />
</colgroup>
<thead>
<tr>
<th></th>
<th><strong>Type</strong></th>
<th><strong>Default</strong></th>
<th><strong>Details</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>code</td>
<td></td>
<td></td>
<td>Code to execute</td>
</tr>
<tr>
<td>timeout</td>
<td>int</td>
<td>5</td>
<td>Maximum run time in seconds before a <code>TimeoutError</code> is
raised</td>
</tr>
</tbody>
</table>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
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
```

</details>

There’s no builtin security here – you should generally use this in a
sandbox, or alternatively prompt before running code. It can handle
multiline function definitions, and pretty much any other normal Python
syntax.

``` python
python("""def factorial(n):
    if n == 0 or n == 1: return 1
    else: return n * factorial(n-1)
factorial(5)""")
```

    120

If the code takes longer than `timeout` then it raises a `TimeoutError`.

``` python
try: python('import time; time.sleep(10)', timeout=1)
except TimeoutError: print('Timed out')
```

### Tool Calling

Many LLM API providers offer tool calling where an LLM can choose to
call a given tool. This is also helpful for structured outputs since the
response from the LLM is contrained to the required arguments of the
tool.

This section will be dedicated to helper functions for calling tools. We
don’t want to allow LLMs to call just any possible function (that would
be a security disaster!) so we create a namespace – that is, a
dictionary of allowable function names to call.

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/funccall.py#L149"
target="_blank" style="float:right; font-size:smaller">source</a>

### mk_ns

>  mk_ns (*funcs_or_objs)

``` python
def sums(a, b): return a + b
ns = mk_ns(sums); ns
```

    {'sums': <function __main__.sums(a, b)>}

``` python
ns['sums'](1, 2)
```

    3

``` python
class Dummy:
    def __init__(self,a): self.a = a
    def __call__(self): return self.a
    def sums(self, a, b): return a + b
    @staticmethod
    def subs(a, b): return a - b
    @classmethod
    def mults(cls, a, b): return a * b
```

``` python
ns = mk_ns(Dummy); ns
```

    {'subs': <function __main__.Dummy.subs(a, b)>,
     'mults': <bound method Dummy.mults of <class '__main__.Dummy'>>,
     'Dummy': __main__.Dummy}

``` python
ns['subs'](1, 2), ns['mults'](3, 2)
```

    (-1, 6)

``` python
d = Dummy(10)
ns = mk_ns(d); ns
```

    {'__call__': <bound method Dummy.__call__ of <__main__.Dummy object>>,
     '__init__': <bound method Dummy.__init__ of <__main__.Dummy object>>,
     'mults': <bound method Dummy.mults of <class '__main__.Dummy'>>,
     'sums': <bound method Dummy.sums of <__main__.Dummy object>>,
     'subs': <staticmethod(<function Dummy.subs>)>}

``` python
ns['subs'](1, 2), ns['mults'](3, 2), ns['sums'](3, 2), ns['__call__']()
```

    (-1, 6, 5, 10)

``` python
ns['__init__'](-99), ns['__call__']()
```

    (None, -99)

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/funccall.py#L158"
target="_blank" style="float:right; font-size:smaller">source</a>

### call_func

>  call_func (fc_name, fc_inputs, ns)

*Call the function `fc_name` with the given `fc_inputs` using namespace
`ns`.*

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def call_func(fc_name, fc_inputs, ns):
    "Call the function `fc_name` with the given `fc_inputs` using namespace `ns`."
    if not isinstance(ns, abc.Mapping): ns = mk_ns(*ns)
    func = ns[fc_name]
    return func(**fc_inputs)
```

</details>

Now when we an LLM responses with the tool to use and its inputs, we can
simply use the same namespace it was given to look up the tool and call
it.

``` python
call_func('sums', {'a': 1, 'b': 2}, ns=[sums])
```

    3

``` python
call_func('subs', {'a': 1, 'b': 2}, ns=mk_ns(d))
```

    -1