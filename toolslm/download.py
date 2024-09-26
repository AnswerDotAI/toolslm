# AUTOGENERATED! DO NOT EDIT! File to edit: ../03_download.ipynb.

# %% auto 0
__all__ = ['clean_md', 'read_md', 'html2md', 'read_html', 'get_llmstxt', 'split_url', 'find_docs', 'read_docs']

# %% ../03_download.ipynb 2
from fastcore.utils import *
from httpx import get
from fastcore.meta import delegates
from llms_txt import *

from html2text import HTML2Text
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# %% ../03_download.ipynb 4
def clean_md(text, rm_comments=True, rm_details=True):
    "Remove comments and `<details>` sections from `text`"
    if rm_comments: text = re.sub(r'\n?<!--.*?-->\n?', '', text, flags=re.DOTALL)
    if rm_details: text = re.sub(r'\n?<details>.*?</details>\n?', '', text, flags=re.DOTALL)
    return text

# %% ../03_download.ipynb 5
@delegates(get)
def read_md(url, rm_comments=True, rm_details=True, **kwargs):
    "Read text from `url` and clean with `clean_docs`"
    return clean_md(get(url, **kwargs).text, rm_comments=rm_comments, rm_details=rm_details)

# %% ../03_download.ipynb 7
def html2md(s:str):
    "Convert `s` from HTML to markdown"
    o = HTML2Text(bodywidth=5000)
    o.ignore_links = True
    o.mark_code = True
    o.ignore_images = True
    return o.handle(s)

# %% ../03_download.ipynb 8
def read_html(url, # URL to read
              sel=None, # Read only outerHTML of CSS selector `sel`
              rm_comments=True, # Removes HTML comments
              rm_details=True # Removes `<details>` tags
             ): # Cleaned markdown
    "Get `url`, optionally selecting CSS selector `sel`, and convert to clean markdown"
    page = get(url).text
    if sel:
        soup = BeautifulSoup(page, 'html.parser')
        page = ''.join(str(el) for el in soup.select(sel))
    md = html2md(page)
    return clean_md(md, rm_comments, rm_details=rm_details)

# %% ../03_download.ipynb 11
def get_llmstxt(url, optional=False, n_workers=None):
    "Get llms.txt file from and expand it with `llms_txt.create_ctx()`"
    if not url.endswith('llms.txt'): return None
    resp = get(url)
    if resp.status_code!=200: return None
    return create_ctx(resp.text, optional=optional, n_workers=n_workers)

# %% ../03_download.ipynb 13
def split_url(url):
    "Split `url` into base, path, and file name, normalising name to '/' if empty"
    parsed = urlparse(url.strip('/'))
    base = f"{parsed.scheme}://{parsed.netloc}"
    path,spl,fname = parsed.path.rpartition('/')
    fname = spl+fname
    if not path and not fname: path='/'
    return base,path,fname

# %% ../03_download.ipynb 15
def _tryget(url):
    "Return response from `url` if `status_code!=404`, otherwise `None`"
    res = get(url)
    return None if res.status_code==404 else url

# %% ../03_download.ipynb 16
def find_docs(url):
    "If available, return LLM-friendly llms.txt context or markdown file location from `url`"
    base,path,fname = split_url(url)
    url = (base+path+fname).strip('/')
    if fname=='/llms.txt': return url
    if Path(fname).suffix in('.md', '.txt', '.rst'): return _tryget(url)
    if '.' in fname: return _tryget(url+'.md') or find_docs(url[:url.rfind('/')])
    res = _tryget(url+'/llms.txt')
    if res: return res
    res = _tryget(url+'/index.md')
    if res: return res
    res = _tryget(url+'/index.html.md')
    if res: return res
    res = _tryget(url+'/index-commonmark.md')
    if res: return res
    parsed_url = urlparse(url)
    if parsed_url.path == '/' or not parsed_url.path: return None
    return find_docs(urljoin(url, '..'))

# %% ../03_download.ipynb 22
def read_docs(url, optional=False, n_workers=None, rm_comments=True, rm_details=True):
    "If available, return LLM-friendly llms.txt context or markdown file response for `url`"
    url = find_docs(url)
    if url.endswith('/llms.txt'): res = get_llmstxt(url, optional=optional, n_workers=n_workers)
    else: res = get(url).text
    return clean_md(res, rm_comments=rm_comments, rm_details=rm_details)
