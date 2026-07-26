r'''Read long Markdown documents by section number: search sections, follow links, and retrieve text by short dotted addresses, so nothing is displayed but what the task needs.

Use this for documentation pages, specifications, reports, and other Markdown. `create_heading_dict(text)` returns a `HeadingDict`: each node maps 1-based section numbers to child nodes, and keeps the complete Markdown for its section in `.text`, with every inline link rendered as `[text][n]` from the document-wide numbering - so displayed sections never spend tokens on URLs. Everything is addressed by short numbers you read off a listing: sections as dotted addresses like `'1.4.5'`, links by a single `n`.

How much to read is a length question. Under roughly 30k characters, just display the whole `.text`: a short document read whole gives an overview nothing else matches, and the link numbering has already cheapened it. Bigger than that, `search()` is the entry point:

    import httpx
    from toolslm.read_md import *

    doc = create_heading_dict(httpx.get(url).text, base=url)
    len(doc.text)                  # < ~30k: display doc.text and be done
    doc.search('hooks?')           # else: `addr title (count)` rows, deepest matching sections
    doc.at('1.4.5').text           # retrieve exactly the sections that matter

`search(pat)` matches a case-insensitive regex line by line (an invalid regex matches literally) and attributes each hit to the deepest section containing it. `paths()` shows the numbered outline when structure itself is the question - `paths(2)` limits depth for a top-level overview. `at('1.4.5')` follows a dotted address from the root; `find(title)` works when a title is known and unique, and raises rather than guess at an ambiguous one. Duplicate sibling titles are fine: numbers keep every section addressable.

For documentation sites with an `llms.txt`, treat it as a table of contents and let the link numbering do the work - parse it, filter the links, follow by number, parse the page, with no URL displayed or retyped at any step:

    toc = create_heading_dict(httpx.get('https://code.claude.com/docs/llms.txt').text)
    toc.links('subagent')                        # a few `[n] Title: description` rows
    l = toc.links('Create custom subagents')[0]
    page = create_heading_dict(toc.follow(l.n), base=l.url)
    page.search('frontmatter')

A `Link` exposes `.n` (its document-wide number), `.txt` (link text), `.url` (the target), `.tail` (the rest of its line, used as an llms.txt description), and `.line` (its document-absolute line number). Its repr deliberately omits `.url`; pass `l.url` as `base` when parsing a page fetched with `follow(l.n)`.

`links(pat='')` on any node lists that section's `Link` rows, filtered by a case-insensitive regex over `.txt`, `.url`, and `.tail`. `follow(n)` returns the link's `.url` content as a plain `str` - fetched for http(s) URLs, read from disk for relative ones, resolved against `base` (recorded automatically by `create_heading_dict_file`; pass `base=` to `create_heading_dict` for text you fetched yourself). Do not fetch `llms-full.txt` or load every linked page unless the task genuinely needs the whole corpus.

A node's `.text` includes its heading and descendants, stopping at the next heading of the same or a higher level. Retrieve shared sections separately when a specific section refers to them. Backtick and tilde fenced blocks are ignored when finding headings and links, so examples containing `#` do not pollute the outline and code samples do not join the link table.

For local files, use `create_heading_dict_file(path)` (`~` ok) rather than reading the text yourself: sections are then directly editable, and relative links resolve. Each node records `start_line` (the heading's 1-based line number in the full document), `view(nums=True)` shows the section with document-absolute line numbers, and `view(lnhashs=True)` shows `lineno|hash|` addresses in exhash's CRC-32 format - valid targets for `file_exhash` commands against that file. Plain `view()` is the source exactly as stored on disk: unlike `.text` it never renumbers links, since an edit address is only good against the file's real bytes. A parsed tree persists while the file may change, so after any edit call `refresh()` on the root for a fresh tree before further edits; a stale address fails loudly at exhash's hash check rather than editing the wrong line.
'''

from .md_hier import HeadingDict, Link, Links, Sections, create_heading_dict, create_heading_dict_file

__all__ = ['HeadingDict', 'Link', 'Links', 'Sections', 'create_heading_dict', 'create_heading_dict_file']
