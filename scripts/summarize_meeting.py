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
summary_filename = raw_filename.replace("raw-", "summary-")
summary_path = f"ai-notes/{summary_filename}"

# ==============================================================================
# Step 2: Read raw file and extract research block
# ==============================================================================
with open(latest_file, "r") as f:
    content = f.read()

# Extract "For AI To Research" section
research_items = ""
if "## For AI To Research" in content:
    parts = content.split("## For AI To Research")
    if len(parts) > 1:
        research_items = parts[1].strip()

# ==============================================================================
# Step 3: Build prompts
# ==============================================================================

summary_prompt = f"""
You are an AI assistant. Summarize this weekly meeting into:

1. High-level summary
2. Key decisions
3. Risks and blockers
4. Action items (use markdown checkboxes)

Meeting content:
{content}
"""

research_prompt = f"""
The following items are things the team wants AI to research.

Items to research:
{research_items}

For each research item:
- Provide a **clear explanation**
- Provide **guidance**
- Provide **best practices**
- Include **references or tool suggestions** if useful
- Format as a clean markdown section

Only output the researched answers.
"""

# ==============================================================================
# Step 4: Gemini API Call Helper
# ==============================================================================
def gemini_call(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    data = { "contents": [{"parts": [{"text": prompt}]}] }
    response = requests.post(url, json=data)

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# ==============================================================================
# Step 5: Generate outputs
# ==============================================================================
meeting_summary = gemini_call(summary_prompt)

research_summary = ""
if research_items.strip() != "":
    research_summary = gemini_call(research_prompt)
else:
    research_summary = "_No AI research items were provided in this meeting._"

# ==============================================================================
# Step 6: Final Output File
# ==============================================================================
full_output = f"""
# Meeting Summary

{meeting_summary}

---

# AI Research Findings

{research_summary}
"""

os.makedirs("ai-notes", exist_ok=True)

with open(summary_path, "w") as f:
    f.write(full_output)

print(f"Created summary file: {summary_path}")
