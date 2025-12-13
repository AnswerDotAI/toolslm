import re
from fastcore.utils import *
__all__ = ['create_heading_dict', 'HeadingDict']

class HeadingDict(dict):
    """A dictionary-like object that also stores the markdown text content."""
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text


def create_heading_dict(text, rm_fenced=True):
    "Create a nested dictionary structure from markdown headings."
    original_text = text
    original_lines = text.splitlines()
    
    # Build line mapping when removing fenced blocks
    if rm_fenced:
        filtered_lines,original_line_map,in_fenced = [],{},False
        for i, line in enumerate(original_lines):
            if line.strip().startswith('```'):
                in_fenced = not in_fenced
                continue
            if not in_fenced:
                original_line_map[len(filtered_lines)] = i
                filtered_lines.append(line)

        lines_for_headings = filtered_lines
    else:
        lines_for_headings = original_lines
        original_line_map = {i: i for i in range(len(original_lines))}

    headings = []

    # Parse headings with their levels and original line numbers
    for idx, line in enumerate(lines_for_headings):
        match = re.match(r'^(#{1,6})\s+\S.*', line)
        if match:
            level = len(match.group(1))
            title = line.strip('#').strip()
            original_line_idx = original_line_map[idx]
            headings.append({'level': level, 'title': title, 'line': original_line_idx})

    # Assign text content to each heading using original lines
    for i, h in enumerate(headings):
        start = h['line']
        # Find the end index: next heading of same or higher level
        for j in range(i + 1, len(headings)):
            if headings[j]['level'] <= h['level']:
                end = headings[j]['line']
                break
        else:
            end = len(original_lines)
        h['content'] = '\n'.join(original_lines[start:end]).strip()

    # Build the nested structure
    result = HeadingDict(original_text)
    stack = [result]
    stack_levels = [0]

    for h in headings:
        # Pop stack until we find the right parent level
        while len(stack) > 1 and stack_levels[-1] >= h['level']:
            stack.pop()
            stack_levels.pop()

        new_dict = HeadingDict(h['content'])
        stack[-1][h['title']] = new_dict
        stack.append(new_dict)
        stack_levels.append(h['level'])

    return result


if __name__=='__main__':
    md_content = """
# User

This is the User section.

## Tokens

Details about tokens.

### Value

The value of tokens.

Some more details.

## Settings

User settings information.

# Admin

Admin section.

## Users

Admin users management.
"""

    result = create_heading_dict(md_content)
    #for key, value in result.items(): print(f'Key: {key}\nValue:\n{value}\n{"-"*40}')

    def test_empty_content():
        md_content = "# Empty Heading"
        result = create_heading_dict(md_content)
        assert 'Empty Heading' in result
        assert result['Empty Heading'].text == '# Empty Heading'
        assert result.text == md_content

    def test_special_characters():
        md_content = "# Heading *With* Special _Characters_!\nContent under heading."
        result = create_heading_dict(md_content)
        assert 'Heading *With* Special _Characters_!' in result
        assert result['Heading *With* Special _Characters_!'].text == '# Heading *With* Special _Characters_!\nContent under heading.'
        assert result.text == md_content

    def test_duplicate_headings():
        md_content = "# Duplicate\n## Duplicate\n### Duplicate\nContent under duplicate headings."
        result = create_heading_dict(md_content)
        assert 'Duplicate' in result
        assert 'Duplicate' in result['Duplicate']
        assert 'Duplicate' in result['Duplicate']['Duplicate']
        assert result['Duplicate']['Duplicate']['Duplicate'].text == '### Duplicate\nContent under duplicate headings.'
        assert result.text == md_content

    def test_no_content():
        md_content = "# No Content Heading\n## Subheading"
        result = create_heading_dict(md_content)
        assert result['No Content Heading'].text == '# No Content Heading\n## Subheading'
        assert result['No Content Heading']['Subheading'].text == '## Subheading'
        assert result.text == md_content

    def test_different_levels():
        md_content = "### Level 3 Heading\nContent at level 3.\n# Level 1 Heading\nContent at level 1."
        result = create_heading_dict(md_content)
        assert 'Level 3 Heading' in result
        assert 'Level 1 Heading' in result
        assert result['Level 3 Heading'].text == '### Level 3 Heading\nContent at level 3.'
        assert result['Level 1 Heading'].text == '# Level 1 Heading\nContent at level 1.'
        assert result.text == md_content

    def test_parent_includes_subheadings():
        md_content = "# Parent\nParent content.\n## Child\nChild content.\n### Grandchild\nGrandchild content."
        result = create_heading_dict(md_content)
        assert result['Parent'].text == '# Parent\nParent content.\n## Child\nChild content.\n### Grandchild\nGrandchild content.'
        assert result['Parent']['Child'].text == '## Child\nChild content.\n### Grandchild\nGrandchild content.'
        assert result['Parent']['Child']['Grandchild'].text == '### Grandchild\nGrandchild content.'
        assert result.text == md_content

    def test_multiple_level2_siblings():
        md_content = "## Sib 1\n## Sib 2\n## Sib 3\n## Sib 4\n## Sib 5'"
        result = create_heading_dict(md_content)
        assert 'Sib 1' in result
        assert 'Sib 2' in result
        assert 'Sib 3' in result
        assert 'Sib 4' in result
        assert "Sib 5'" in result
        assert result.text == md_content

    def test_code_chunks_escaped():
        md_content = "# Parent\nParent content.\n## Child\nChild content.\n```python\n# Code comment\nprint('Hello, world!')\n```"
        result = create_heading_dict(md_content)
        assert 'Code comment' not in str(result)
        assert result.text == md_content

    test_empty_content()
    test_special_characters()
    test_duplicate_headings()
    test_no_content()
    test_different_levels()
    test_parent_includes_subheadings()
    test_multiple_level2_siblings()
    test_code_chunks_escaped()
    print('tests passed')

    def test_nested_headings():
        md_content = "# Parent\nParent content.\n## Child\nChild content.\n### Grandchild\nGrandchild content."
        result = create_heading_dict(md_content)
        assert 'Child' in result['Parent']
        assert 'Grandchild' in result['Parent']['Child']

    def test_code_chunks_escaped():
        md_content = "# Parent\nParent content.\n## Child\nChild content.\n```python\n# Code comment\nprint('Hello, world!')\n```"
        result = create_heading_dict(md_content)
        assert 'Code comment' not in result

    def test_fenced_blocks_preserved_in_text():
        md_content = """# Section
Content before code.

```python
# This heading should be ignored for structure
def hello():
    print("Hello, world!")
```

More content after code."""
        result = create_heading_dict(md_content)
        # Fenced code should be preserved in text content
        assert '```python' in result['Section'].text
        assert 'def hello():' in result['Section'].text
        assert '```' in result['Section'].text
        # But headings inside fenced blocks should not create structure
        assert 'This heading should be ignored for structure' not in result['Section']

    test_nested_headings()
    test_code_chunks_escaped()
    test_fenced_blocks_preserved_in_text()

    def test_multiple_h1s():
        md_content = "# First H1\n# Second H1\n# Third H1"
        result = create_heading_dict(md_content)
        assert 'First H1' in result
        assert 'Second H1' in result
        assert 'Third H1' in result
        assert result['First H1'] == {}
        assert result['Second H1'] == {}
        assert result['Third H1'] == {}

    def test_skip_levels_down():
        md_content = "# Root\n## Level2\n#### Level4"
        result = create_heading_dict(md_content)
        assert 'Root' in result
        assert 'Level2' in result['Root']
        assert 'Level4' in result['Root']['Level2']

    def test_skip_levels_up():
        md_content = "# Root\n#### Deep\n## Back to 2"
        result = create_heading_dict(md_content)
        assert 'Root' in result
        assert 'Deep' in result['Root']
        assert 'Back to 2' in result['Root']
        assert result['Root']['Deep'] == {}
        assert result['Root']['Back to 2'] == {}

    def test_non_h1_start():
        md_content = "### Starting at 3\n## Going to 2\n# Finally 1"
        result = create_heading_dict(md_content)
        assert 'Starting at 3' in result
        assert 'Going to 2' in result
        assert 'Finally 1' in result

    test_multiple_h1s()
    test_skip_levels_down()
    test_skip_levels_up()
    test_non_h1_start()

    # Edge case tests
    def test_empty_input():
        result = create_heading_dict("")
        assert result == {}
        assert result.text == ""

    def test_whitespace_only():
        result = create_heading_dict("   \n\t  \n   ")
        assert result == {}
        assert result.text == "   \n\t  \n   "

    def test_malformed_headings():
        # Too many #s (matches max 6)
        md_content = "####### Too Many\nContent"
        result = create_heading_dict(md_content)
        assert 'Too Many' not in result
        assert result.text == md_content

    def test_unicode_and_emojis():
        # Unicode characters
        md_content = "# Café & Naïve\nContent with unicode\n## 中文标题\nChinese content"
        result = create_heading_dict(md_content)
        assert 'Café & Naïve' in result
        assert '中文标题' in result['Café & Naïve']
        assert result.text == md_content

        # Emojis
        md_content = "# 🚀 Rocket Heading\nRocket content\n## 💻 Computer\nComputer content"
        result = create_heading_dict(md_content)
        assert '🚀 Rocket Heading' in result
        assert '💻 Computer' in result['🚀 Rocket Heading']
        assert result.text == md_content

    def test_fenced_blocks_between_headings():
        md_content = """# First Header
Content here.

```python
# A comment that should be ignored for structure
def example():
    pass
```

# Second Header
This content belongs to Second Header."""
        result = create_heading_dict(md_content)
        assert "def example():" not in result['Second Header'].text
        assert result['Second Header'].text == "# Second Header\nThis content belongs to Second Header."

    test_empty_input()
    test_whitespace_only()
    test_malformed_headings()
    test_unicode_and_emojis()
    test_fenced_blocks_between_headings()
    print('tests passed')

