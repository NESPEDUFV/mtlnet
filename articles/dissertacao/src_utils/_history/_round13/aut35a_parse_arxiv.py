import re, html, sys

path = sys.argv[1]
s = open(path, encoding='utf-8', errors='replace').read()

CLOSE = '<' + '/'
pats = [
    ('TITLE',    r'class="title[^"]*"[^' + '>' + r']*' + '>' + r'(.*?)' + CLOSE + 'h1' + '>'),
    ('AUTHORS',  r'class="authors"' + '>' + r'(.*?)' + CLOSE + 'div' + '>'),
    ('ABSTRACT', r'class="abstract[^"]*"' + '>' + r'(.*?)' + CLOSE + 'blockquote' + '>'),
    ('DATELINE', r'class="dateline"' + '>' + r'(.*?)' + CLOSE + 'div' + '>'),
    ('JREF',     r'class="tablecell jref"' + '>' + r'(.*?)' + CLOSE + 'td' + '>'),
    ('DOI',      r'class="tablecell doi"' + '>' + r'(.*?)' + CLOSE + 'td' + '>'),
    ('COMMENTS', r'class="tablecell comments[^"]*"' + '>' + r'(.*?)' + CLOSE + 'td' + '>'),
    ('SUBJECTS', r'class="tablecell subjects"' + '>' + r'(.*?)' + CLOSE + 'td' + '>'),
    ('HISTORY',  r'class="submission-history"' + '>' + r'(.*?)' + CLOSE + 'div' + '>'),
]
tagre = re.compile(r'<' + r'[^' + '>' + r']+' + '>')
for label, pat in pats:
    m = re.search(pat, s, re.S)
    if m:
        t = tagre.sub(' ', m.group(1))
        print('### ' + label + ' :: ' + ' '.join(html.unescape(t).split()))
    else:
        print('### ' + label + ' :: (ABSENT)')
