import re
from fastcore.utils import *
__all__ = ['markdown_to_dict', 'create_heading_dict']

def markdown_to_dict(markdown_content):
    def clean_heading(text): return re.sub(r'[^A-Za-z0-9 ]+', '', text).strip()

    lines = markdown_content.splitlines()
    headings = []
    in_code_block = False

    # Parse headings with their levels and line numbers
    for idx, line in enumerate(lines):
        # Toggle code block state when encountering fence
        if line.strip().startswith('```'): in_code_block = not in_code_block
        
        # Only detect headings when not in a code block
        if in_code_block: continue
        match = re.match(r'^(#{1,6})\s*(.*)', line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({'level': level, 'text': text, 'line': idx})

    # Assign content to each heading, including subheadings
    for i, h in enumerate(headings):
        start = h['line']  # Include the heading line itself
        # Find the end index: next heading of same or higher level
        for j in range(i + 1, len(headings)):
            if headings[j]['level'] <= h['level']:
                end = headings[j]['line']
                break
        else: end = len(lines)
        h['content'] = '\n'.join(lines[start:end]).strip()

    # Build the dictionary with hierarchical keys
    result,stack = {},[]
    first_level = headings[0]['level']
    for h in headings:
        stack = stack[:h['level'] - first_level] + [clean_heading(h['text'])]
        key = '.'.join(stack)
        result[key] = h['content']
    return dict2obj(result)

def create_heading_dict(text):
    text = re.sub(r'```[\s\S]*?```', '', text)
    headings = re.findall(r'^#+.*', text, flags=re.MULTILINE)
    result = {}
    stack = [result]
    prev_level = 0

    for heading in headings:
        level = heading.count('#')
        title = heading.strip('#').strip()
        while level <= prev_level:
            stack.pop()
            prev_level -= 1
        new_dict = {}
        stack[-1][title] = new_dict
        stack.append(new_dict)
        prev_level = level
    return dict2obj(result)


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

    result = markdown_to_dict(md_content)
    #for key, value in result.items(): print(f'Key: {key}\nValue:\n{value}\n{"-"*40}')

    def test_empty_content():
        md_content = "# Empty Heading"
        result = markdown_to_dict(md_content)
        assert result['Empty Heading'] == '# Empty Heading'

    def test_special_characters():
        md_content = "# Heading *With* Special _Characters_!\nContent under heading."
        result = markdown_to_dict(md_content)
        assert 'Heading With Special Characters' in result
        assert result['Heading With Special Characters'] == '# Heading *With* Special _Characters_!\nContent under heading.'

    def test_duplicate_headings():
        md_content = "# Duplicate\n## Duplicate\n### Duplicate\nContent under duplicate headings."
        result = markdown_to_dict(md_content)
        assert 'Duplicate' in result
        assert 'Duplicate.Duplicate' in result
        assert 'Duplicate.Duplicate.Duplicate' in result
        assert result['Duplicate.Duplicate.Duplicate'] == '### Duplicate\nContent under duplicate headings.'

    def test_no_content():
        md_content = "# No Content Heading\n## Subheading"
        result = markdown_to_dict(md_content)
        assert result['No Content Heading'] == '# No Content Heading\n## Subheading'
        assert result['No Content Heading.Subheading'] == '## Subheading'

    def test_different_levels():
        md_content = "### Level 3 Heading\nContent at level 3.\n# Level 1 Heading\nContent at level 1."
        result = markdown_to_dict(md_content)
        assert 'Level 3 Heading' in result
        assert 'Level 1 Heading' in result
        assert result['Level 3 Heading'] == '### Level 3 Heading\nContent at level 3.'
        assert result['Level 1 Heading'] == '# Level 1 Heading\nContent at level 1.'

    def test_parent_includes_subheadings():
        md_content = "# Parent\nParent content.\n## Child\nChild content.\n### Grandchild\nGrandchild content."
        result = markdown_to_dict(md_content)
        assert result['Parent'] == '# Parent\nParent content.\n## Child\nChild content.\n### Grandchild\nGrandchild content.'
        assert result['Parent.Child'] == '## Child\nChild content.\n### Grandchild\nGrandchild content.'
        assert result['Parent.Child.Grandchild'] == '### Grandchild\nGrandchild content.'

    def test_multiple_level2_siblings():
        md_content = "##Sib 1\n##Sib 2\n##Sib 3\n##Sib 4\n##Sib 5'"
        result = markdown_to_dict(md_content)
        assert 'Sib 1' in result
        assert 'Sib 2' in result
        assert 'Sib 3' in result
        assert 'Sib 4' in result
        assert 'Sib 5' in result
        
    def test_code_chunks_escaped():
        md_content = "# Parent\nParent content.\n## Child\nChild content.\n```python\n# Code comment\nprint('Hello, world!')\n```"
        result = markdown_to_dict(md_content)
        assert 'Code comment' not in result
        assert "# Code comment" in result['Parent.Child']

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
    
    test_nested_headings()
    test_code_chunks_escaped()
    print('tests passed')