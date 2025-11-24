import datetime
import os
import glob
import string

# ===================================================================================
# Create Raw Meeting Note Template (with suffix support + research section)
# ===================================================================================

today = datetime.date.today()
date_str = str(today)

# Base filename (no suffix yet)
base_filename = f"raw-{date_str}.md"
base_path = f"original-notes/{base_filename}"

# Determine correct filename (support a, b, c… suffixes)
if not os.path.exists(base_path):
    filename = base_filename
else:
    pattern = f"original-notes/raw-{date_str}-*.md"
    existing = sorted(glob.glob(pattern))

    if not existing:
        filename = f"raw-{date_str}-a.md"
    else:
        last_file = existing[-1]
        last_suffix = last_file.split("-")[-1].replace(".md", "")
        next_suffix = string.ascii_lowercase[string.ascii_lowercase.index(last_suffix) + 1]
        filename = f"raw-{date_str}-{next_suffix}.md"

path = f"original-notes/{filename}"

# Template with NEW "For AI To Research" section
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

---

## For AI To Research
Write items here that AI should research and provide answers for.

- 
"""

os.makedirs("original-notes", exist_ok=True)

with open(path, "w") as f:
    f.write(template)

print(f"Created: {path}")
