r'''Read long Markdown documents by heading, so an agent can inspect an outline, retrieve only the sections it needs, or get line addresses for editing sections of a local file in place.

Use this for documentation pages, specifications, reports, and other Markdown that is too long to read efficiently as one flat string. `create_heading_dict(text)` returns a `HeadingDict`: each node maps child heading titles to more nodes and keeps the complete Markdown for its section in `.text`.

Typical workflow:

    import httpx
    from toolslm.read_md import *

    text = httpx.get('https://developers.openai.com/codex/hooks.md').text
    doc = create_heading_dict(text)
    doc.paths()
    doc.at('Hooks', 'Hooks', 'SessionStart').text

Inspect `paths()` before retrieving sections. Do not display or slice the full Markdown first; parsing it immediately keeps the outline cheap and preserves each section as a semantic unit. Use `at(*headings)` when you know the path, especially when titles repeat. Use `find(title)` only when the title is unique; it raises for missing or ambiguous titles rather than choosing silently.

For documentation sites with an `llms.txt`, treat it as a table of contents: fetch it, choose the relevant linked Markdown page, then parse that targeted page. Do not fetch `llms-full.txt` or load every linked page unless the task genuinely needs the whole corpus.

A node's `.text` includes its heading and descendants, stopping at the next heading of the same or a higher level. Retrieve shared sections separately when an event-specific section refers to them, for example:

    common_in = doc.at('Hooks', 'Common input fields').text
    common_out = doc.at('Hooks', 'Common output fields').text
    session = doc.find('SessionStart').text

Backtick and tilde fenced blocks are ignored when finding headings, so examples containing `#` do not pollute the outline. Duplicate sibling headings raise instead of silently overwriting a section; the same title under different parents is fine and remains addressable by path.

For local files, use `create_heading_dict_file(path)` (`~` ok) rather than reading the text yourself: sections are then directly editable. Each node records `start_line` (the heading's 1-based line number in the full document), `view(nums=True)` shows the section with document-absolute line numbers, and `view(lnhashs=True)` shows `lineno|hash|` addresses in exhash's CRC-32 format - valid targets for `exhash_file` commands against that file. Plain `view()` is just `.text`. A parsed tree persists while the file may change, so after any edit call `refresh()` on the root for a fresh tree before further edits; a stale address fails loudly at exhash's hash check rather than editing the wrong line.
'''

from .md_hier import HeadingDict, create_heading_dict, create_heading_dict_file

__all__ = ['HeadingDict', 'create_heading_dict', 'create_heading_dict_file']
