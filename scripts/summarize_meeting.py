import os
import glob
import re
import requests

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash-lite"

# ==============================================================================
# Helper: Correct suffix sorting ("" < "a" < "b" ...)
# ==============================================================================
def extract_sort_key(path):
    name = os.path.basename(path)
    match = re.match(r"raw-(\d{4}-\d{2}-\d{2})(?:-([a-z]))?\.md", name)
    if not match:
        return ("0000-00-00", "")
    date_str, suffix = match.groups()
    suffix = suffix or ""
    return (date_str, suffix)

# ==============================================================================
# Step 1: Identify newest raw note
# ==============================================================================
files = glob.glob("original-notes/raw-*.md")
files_sorted = sorted(files, key=extract_sort_key)

latest_file = files_sorted[-1]
raw_filename = os.path.basename(latest_file)

# Base summary filename (OPTION C)
base_summary_name = raw_filename.replace("raw-", "summary-")
summary_dir = "ai-notes"
os.makedirs(summary_dir, exist_ok=True)

# ==============================================================================
# Step 2: Create versioned summary name (summary-v2.md, summary-v3.md…)
# ==============================================================================
def get_available_summary_filename(base_name):
    base_path = os.path.join(summary_dir, base_name)

    # If file does not exist, use it directly
    if not os.path.exists(base_path):
        return base_path

    # Otherwise start generating v2, v3, v4
    name_no_ext = base_name.replace(".md", "")
    counter = 2

    while True:
        new_filename = f"{name_no_ext}-v{counter}.md"
        new_path = os.path.join(summary_dir, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1

summary_path = get_available_summary_filename(base_summary_name)

# ==============================================================================
# Step 3: Extract research section from raw file
# ==============================================================================
with open(latest_file, "r") as f:
    content = f.read()

research_items = ""
if "## For AI To Research" in content:
    parts = content.split("## For AI To Research")
    if len(parts) > 1:
        research_items = parts[1].strip()

# ==============================================================================
# Step 4: Build AI prompts
# ==============================================================================
summary_prompt = f"""
Summarize this weekly meeting into:

1. High-level summary
2. Key decisions
3. Risks and blockers
4. Action items (markdown checkboxes)

Meeting content:
{content}
"""

research_prompt = f"""
Below are items the team wants AI to research.

Items:
{research_items}

For each research item:
- Explain the concept clearly
- Provide best practices
- Provide recommendations
- Provide tool suggestions (if relevant)
- Write clean markdown

Only output the researched answers.
"""

# ==============================================================================
# Step 5: Gemini API Helper
# ==============================================================================
def gemini_call(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    data = { "contents": [{"parts": [{"text": prompt}]}] }
    response = requests.post(url, json=data)
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# ==============================================================================
# Step 6: Generate AI outputs
# ==============================================================================
meeting_summary = gemini_call(summary_prompt)

if research_items.strip() != "":
    research_summary = gemini_call(research_prompt)
else:
    research_summary = "_No AI research items were provided in this meeting._"

# ==============================================================================
# Step 7: Final Markdown Output
# ==============================================================================
full_output = f"""
# Meeting Summary

{meeting_summary}

---

# AI Research Findings

{research_summary}
"""

with open(summary_path, "w") as f:
    f.write(full_output)

print(f"Created summary file: {summary_path}")
