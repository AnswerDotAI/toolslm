# xml source


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Setup

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/xml.py#L19"
target="_blank" style="float:right; font-size:smaller">source</a>

### json_to_xml

>  json_to_xml (d:dict, rnm:str)

*Convert `d` to XML.*

<table>
<thead>
<tr>
<th></th>
<th><strong>Type</strong></th>
<th><strong>Details</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>d</td>
<td>dict</td>
<td>JSON dictionary to convert</td>
</tr>
<tr>
<td>rnm</td>
<td>str</td>
<td>Root name</td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>str</strong></td>
<td></td>
</tr>
</tbody>
</table>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def json_to_xml(d:dict, # JSON dictionary to convert
                rnm:str # Root name
               )->str:
    "Convert `d` to XML."
    root = ET.Element(rnm)
    def build_xml(data, parent):
        if isinstance(data, dict):
            for key, value in data.items(): build_xml(value, ET.SubElement(parent, key))
        elif isinstance(data, list):
            for item in data: build_xml(item, ET.SubElement(parent, 'item'))
        else: parent.text = str(data)
    build_xml(d, root)
    ET.indent(root)
    return ET.tostring(root, encoding='unicode')
```

</details>

JSON doesn’t map as nicely to XML as the data structure used in
`fastcore.xml`, but for simple XML trees it can be convenient – for
example:

``` python
a = dict(surname='Howard', firstnames=['Jeremy','Peter'],
         address=dict(state='Queensland',country='Australia'))
hl_md(json_to_xml(a, 'person'))
```

``` xml
<person>
  <surname>Howard</surname>
  <firstnames>
    <item>Jeremy</item>
    <item>Peter</item>
  </firstnames>
  <address>
    <state>Queensland</state>
    <country>Australia</country>
  </address>
</person>
```

## Including documents

According [to
Anthropic](https://docs.anthropic.com/claude/docs/long-context-window-tips),
“*it’s essential to structure your prompts in a way that clearly
separates the input data from the instructions*”. They recommend using
something like the following:

``` xml
Here are some documents for you to reference for your task:
    
<documents>
<document index="1">
<source>
(URL, file name, hash, etc)
</source>
<document_content>
(the text content)
</document_content>
</document>
</documents>
```

We will create some small helper functions to make it easier to generate
context in this format, although we’re use `<src>` instead of `<source>`
to avoid conflict with that HTML tag. Although it’s based on Anthropic’s
recommendation, it’s likely to work well with other models too.

<details open class="code-fold">
<summary>Exported source</summary>

``` python
doctype = namedtuple('doctype', ['src', 'content'])
```

</details>

We’ll use `doctype` to store our pairs.

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def _add_nls(s):
    "Add newlines to start and end of `s` if missing"
    if not s: return s
    if s[ 0]!='\n': s = '\n'+s
    if s[-1]!='\n': s = s+'\n'
    return s
```

</details>

Since Anthropic’s example shows newlines before and after each tag,
we’ll do the same.

``` python
to_xml(Src('a'))
```

    '<src>a</src>'

``` python
to_xml(Document('a'))
```

    '<document>a</document>'

``` python
to_xml(Documents('a'))
```

    '<documents>a</documents>'

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/xml.py#L46"
target="_blank" style="float:right; font-size:smaller">source</a>

### mk_doctype

>  mk_doctype (content:str, src:Optional[str]=None)

*Create a `doctype` named tuple*

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
<td>content</td>
<td>str</td>
<td></td>
<td>The document content</td>
</tr>
<tr>
<td>src</td>
<td>Optional</td>
<td>None</td>
<td>URL, filename, etc; defaults to <code>md5(content)</code> if not
provided</td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>namedtuple</strong></td>
<td></td>
<td></td>
</tr>
</tbody>
</table>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def mk_doctype(content:str,  # The document content
           src:Optional[str]=None # URL, filename, etc; defaults to `md5(content)` if not provided
          ) -> namedtuple:
    "Create a `doctype` named tuple"
    if src is None: src = hashlib.md5(content.encode()).hexdigest()[:8]
    return doctype(_add_nls(str(src).strip()), _add_nls(content.strip()))
```

</details>

This is a convenience wrapper to ensure that a `doctype` has the needed
information in the right format.

``` python
doc = 'This is a "sample"'
mk_doctype(doc)
```

    doctype(src='\n47e19350\n', content='\nThis is a "sample"\n')

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/xml.py#L54"
target="_blank" style="float:right; font-size:smaller">source</a>

### mk_doc

>  mk_doc (index:int, content:str, src:Optional[str]=None, **kwargs)

*Create an `ft` format tuple for a single doc in Anthropic’s recommended
format*

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
<td>index</td>
<td>int</td>
<td></td>
<td>The document index</td>
</tr>
<tr>
<td>content</td>
<td>str</td>
<td></td>
<td>The document content</td>
</tr>
<tr>
<td>src</td>
<td>Optional</td>
<td>None</td>
<td>URL, filename, etc; defaults to <code>md5(content)</code> if not
provided</td>
</tr>
<tr>
<td>kwargs</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>tuple</strong></td>
<td></td>
<td></td>
</tr>
</tbody>
</table>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def mk_doc(index:int,  # The document index
           content:str,  # The document content
           src:Optional[str]=None, # URL, filename, etc; defaults to `md5(content)` if not provided
           **kwargs
          ) -> tuple:
    "Create an `ft` format tuple for a single doc in Anthropic's recommended format"
    dt = mk_doctype(content, src)
    content = Document_content(NotStr(dt.content))
    src = Src(NotStr(dt.src))
    return Document(src, content, index=index, **kwargs)
```

</details>

We can now generate XML for one document in the suggested format:

``` python
mk_doc(1, doc, title="test")
```

``` html
<document index="1" title="test"><src>
47e19350
</src><document-content>
This is a "sample"
</document-content></document>
```

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/xml.py#L66"
target="_blank" style="float:right; font-size:smaller">source</a>

### docs_xml

>  docs_xml (docs:list[str], srcs:Optional[list]=None, prefix:bool=True,
>                details:Optional[list]=None)

*Create an XML string containing `docs` in Anthropic’s recommended
format*

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
<td>docs</td>
<td>list</td>
<td></td>
<td>The content of each document</td>
</tr>
<tr>
<td>srcs</td>
<td>Optional</td>
<td>None</td>
<td>URLs, filenames, etc; each one defaults to <code>md5(content)</code>
if not provided</td>
</tr>
<tr>
<td>prefix</td>
<td>bool</td>
<td>True</td>
<td>Include Anthropic’s suggested prose intro?</td>
</tr>
<tr>
<td>details</td>
<td>Optional</td>
<td>None</td>
<td>Optional list of dicts with additional attrs for each doc</td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>str</strong></td>
<td></td>
<td></td>
</tr>
</tbody>
</table>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def docs_xml(docs:list[str],  # The content of each document
             srcs:Optional[list]=None,  # URLs, filenames, etc; each one defaults to `md5(content)` if not provided
             prefix:bool=True, # Include Anthropic's suggested prose intro?
             details:Optional[list]=None # Optional list of dicts with additional attrs for each doc
            )->str:
    "Create an XML string containing `docs` in Anthropic's recommended format"
    pre = 'Here are some documents for you to reference for your task:\n\n' if prefix else ''
    if srcs is None: srcs = [None]*len(docs)
    if details is None: details = [{}]*len(docs)
    docs = (mk_doc(i+1, d, s, **kw) for i,(d,s,kw) in enumerate(zip(docs,srcs,details)))
    return pre + to_xml(Documents(docs))
```

</details>

Putting it all together, we have our final XML format:

``` python
docs = [doc, 'And another one']
srcs = [None, 'doc.txt']
print(docs_xml(docs, srcs))
```

    Here are some documents for you to reference for your task:

    <documents><document index="1"><src>
    47e19350
    </src><document-content>
    This is a "sample"
    </document-content></document><document index="2"><src>
    doc.txt
    </src><document-content>
    And another one
    </document-content></document></documents>

## Context creation

Now that we can generate Anthropic’s XML format, let’s make it easy for
a few common cases.

### File list to context

For generating XML context from files, we’ll just read them as text and
use the file names as `src`.

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/xml.py#L79"
target="_blank" style="float:right; font-size:smaller">source</a>

### files2ctx

>  files2ctx (fnames:list[typing.Union[str,pathlib.Path]], prefix:bool=True)

<table>
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
<td>fnames</td>
<td>list</td>
<td></td>
<td>List of file names to add to context</td>
</tr>
<tr>
<td>prefix</td>
<td>bool</td>
<td>True</td>
<td>Include Anthropic’s suggested prose intro?</td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>str</strong></td>
<td></td>
<td><strong>XML for LM context</strong></td>
</tr>
</tbody>
</table>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
def files2ctx(
    fnames:list[Union[str,Path]], # List of file names to add to context
    prefix:bool=True # Include Anthropic's suggested prose intro?
)->str: # XML for LM context
    fnames = [Path(o) for o in fnames]
    contents = [o.read_text() for o in fnames]
    return docs_xml(contents, fnames, prefix=prefix)
```

</details>

``` python
fnames = ['samples/sample_core.py', 'samples/sample_styles.css']
hl_md(files2ctx(fnames))
```

``` xml
Here are some documents for you to reference for your task:

<documents><document index="1"><src>
samples/sample_core.py
</src><document-content>
import inspect
empty = inspect.Parameter.empty
models = 'claude-3-opus-20240229','claude-3-sonnet-20240229','claude-3-haiku-20240307'
</document-content></document><document index="2"><src>
samples/sample_styles.css
</src><document-content>
.cell { margin-bottom: 1rem; }
.cell > .sourceCode { margin-bottom: 0; }
.cell-output > pre { margin-bottom: 0; }
</document-content></document></documents>
```

### Folder to context

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/toolslm/blob/main/toolslm/xml.py#L89"
target="_blank" style="float:right; font-size:smaller">source</a>

### folder2ctx

>  folder2ctx (folder:Union[str,pathlib.Path], prefix:bool=True,
>                  recursive:bool=True, symlinks:bool=True, file_glob:str=None,
>                  file_re:str=None, folder_re:str=None,
>                  skip_file_glob:str=None, skip_file_re:str=None,
>                  skip_folder_re:str=None, func:callable=<function join>,
>                  ret_folders:bool=False)

<table>
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
<td>folder</td>
<td>Union</td>
<td></td>
<td>Folder name containing files to add to context</td>
</tr>
<tr>
<td>prefix</td>
<td>bool</td>
<td>True</td>
<td>Include Anthropic’s suggested prose intro?</td>
</tr>
<tr>
<td>recursive</td>
<td>bool</td>
<td>True</td>
<td>search subfolders</td>
</tr>
<tr>
<td>symlinks</td>
<td>bool</td>
<td>True</td>
<td>follow symlinks?</td>
</tr>
<tr>
<td>file_glob</td>
<td>str</td>
<td>None</td>
<td>Only include files matching glob</td>
</tr>
<tr>
<td>file_re</td>
<td>str</td>
<td>None</td>
<td>Only include files matching regex</td>
</tr>
<tr>
<td>folder_re</td>
<td>str</td>
<td>None</td>
<td>Only enter folders matching regex</td>
</tr>
<tr>
<td>skip_file_glob</td>
<td>str</td>
<td>None</td>
<td>Skip files matching glob</td>
</tr>
<tr>
<td>skip_file_re</td>
<td>str</td>
<td>None</td>
<td>Skip files matching regex</td>
</tr>
<tr>
<td>skip_folder_re</td>
<td>str</td>
<td>None</td>
<td>Skip folders matching regex,</td>
</tr>
<tr>
<td>func</td>
<td>callable</td>
<td>join</td>
<td>function to apply to each matched file</td>
</tr>
<tr>
<td>ret_folders</td>
<td>bool</td>
<td>False</td>
<td>return folders, not just files</td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>str</strong></td>
<td></td>
<td><strong>XML for Claude context</strong></td>
</tr>
</tbody>
</table>

<details open class="code-fold">
<summary>Exported source</summary>

``` python
@delegates(globtastic)
def folder2ctx(
    folder:Union[str,Path], # Folder name containing files to add to context
    prefix:bool=True, # Include Anthropic's suggested prose intro?
    **kwargs # Passed to `globtastic`
)->str: # XML for Claude context
    fnames = globtastic(folder, **kwargs)
    return files2ctx(fnames, prefix=prefix)
```

</details>

``` python
print(folder2ctx('samples', prefix=False, file_glob='*.py'))
```

    <documents><document index="1"><src>
    samples/sample_core.py
    </src><document-content>
    import inspect
    empty = inspect.Parameter.empty
    models = 'claude-3-opus-20240229','claude-3-sonnet-20240229','claude-3-haiku-20240307'
    </document-content></document></documents>

<div>

> **Tip**
>
> After you install `toolslm`,
> [`folder2ctx`](https://AnswerDotAI.github.io/toolslm/xml.html#folder2ctx)
> becomes available from the command line. You can see how to use it
> with the following command:
>
> ``` bash
> folder2ctx -h
> ```

</div>