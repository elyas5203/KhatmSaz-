import glob
import re

files = glob.glob('migrations/versions/*.py')
down_revs = set()
rev_map = {}
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        text = file.read()
        rev_m = re.search(r"revision[:\s\w]*=\s*'([a-zA-Z0-9_]+)'", text)
        down_m = re.search(r"down_revision[:\s\w,\[\]]*=\s*'([a-zA-Z0-9_]+)'", text)
        
        if rev_m:
            rev = rev_m.group(1)
            down = down_m.group(1) if down_m and down_m.group(1) != 'None' else None
            rev_map[rev] = f
            if down:
                down_revs.add(down)

heads = set(rev_map.keys()) - down_revs
print("HEAD IS", list(heads)[0] if heads else None)
