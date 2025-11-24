import datetime
import os
import glob
import string

today = datetime.date.today()
date_str = str(today)

base_filename = f"raw-{date_str}.md"
base_path = f"documentation/meetings/raw-notes/{base_filename}"

if not os.path.exists(base_path):
    filename = base_filename
else:
    pattern = f"documentation/meetings/raw-notes/raw-{date_str}-*.md"
    existing = sorted(glob.glob(pattern))

    if not existing:
        filename = f"raw-{date_str}-a.md"
    else:
        last_file = existing[-1]
        last_suffix = last_file.split("-")[-1].replace(".md", "")
        next_suffix = string.ascii_lowercase[string.ascii_lowercase.index(last_suffix) + 1]
        filename = f"raw-{date_str}-{next_suffix}.md"

path = f"documentation/meetings/raw-notes/{filename}"

template = f"""# Weekly Meeting Notes — {today}

## Attendees
-

## Updates
-

## Discussion Topics
-

## Decisions
-

## Action Items
- [ ] Example item
"""

os.makedirs("documentation/meetings/raw-notes", exist_ok=True)

with open(path, "w") as f:
    f.write(template)

print(f"Created: {path}")
