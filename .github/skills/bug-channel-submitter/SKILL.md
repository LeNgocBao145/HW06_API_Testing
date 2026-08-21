---
name: bug-channel-submitter
description: Decoupled bug reporting tool that submits findings from a local log to any destination channel (Google Forms, Jira, Slack, GitHub Issues) with deduplication checks, dynamic form-field discovery, and tab isolation.
---

# Universal Bug Channel Submitter

## Parameters & Defaults
- Log File: `--log-file` (Default: `agent_artifacts/bug-channel-submitter/bug_and_usability_findings_log.md`)
- Channel Type: `--channel-type` (Options: `web_form` | `jira` | `slack` | `github_issues`)
- Channel Target: `--channel-target` (URL or Project Key or Channel ID)
- Allow Duplicate: `--allow-duplicate` (Default: `false`)
- Mapping Cache File: `--mapping-cache-file` (Default: `agent_artifacts/bug-channel-submitter/bug_channel_field_mappings.json`)

---

## Step 0 — Channel Adapter Initialization
1. Inspect `--channel-type` and `--channel-target`:
   - **`web_form`**: Verify a browser-automation MCP tool is available (e.g. Playwright MCP —
     tools like `browser_navigate`, `browser_snapshot`, `browser_fill`/`browser_type`,
     `browser_select_option`, `browser_click`, `browser_tab_new`, `browser_tab_close`).
     If no such MCP is connected, stop and ask the user to connect one before proceeding.
   - **`jira` / `slack` / `github_issues`**: Verify corresponding MCP or API credentials in `.env`.
2. Parse workspace `.env` for required credentials (e.g., `STUDENT_EMAIL`, `JIRA_TOKEN`, `SLACK_WEBHOOK`). Prompt user if missing.

## Step 1 — Deduplication Check & Bug Selection
1. Read `<LOG_FILE>` and parse all bug entries.
2. Filter for candidate bugs:
   - For each bug, check `Submission Status` and `Submitted Channel`.
   - **If ALREADY SUBMITTED to this target:**
     - If `--allow-duplicate` is `false`, **PAUSE** and prompt user in chat:
       > *"Bug **[Bug ID]** was already submitted to [Target] at [Timestamp]. Do you want to submit a duplicate? (y/N)"*
     - If user declines, skip to the next bug.
3. Queue up all validated unsubmitted bugs for dispatch.

## Step 2 — Dispatch per Channel Type

### Option A: `web_form` (Google Form / Microsoft Form / Web Portal)

The agent never assumes a fixed field schema. Every unfamiliar form is
**discovered first, then mapped, then filled** — never the reverse.

For each queued bug:

1. Open a **NEW browser tab** (`browser_tab_new` / equivalent new target context).
2. Navigate to `--channel-target` URL.
3. **Field Discovery Pass** (run once per distinct form URL, not per bug):
   - Take a `browser_snapshot` (accessibility tree) of the page.
   - Enumerate every input-capable element: text input, textarea, radio group,
     checkbox, dropdown/select, file upload.
   - For each, record: `{field_id (element ref), label_text, field_type, options[] (if radio/dropdown/checkbox)}`.
   - Build a `discovered_fields` list from this pass.
4. **Check Mapping Cache:**
   - Look up `--mapping-cache-file` for an entry keyed by the form URL (or a hash of the
     discovered field labels, so a cache entry is invalidated if the form changes).
   - If a cached mapping exists, skip to step 6 using the cached `field → bug_attribute` map.
5. **Dynamic Field Mapping** (only if no cache hit):
   - For text/textarea fields, match `label_text` to a bug attribute by keyword/synonym,
     case-insensitive substring match. Reference synonyms (extend as needed):
     - "email" → Student Email
     - "screen", "scenario", "page" → Screen ID / Scenario
     - "type", "category", "kind" → Type (Bug | Usability)
     - "description", "detail", "summary" → Description
     - "step", "reproduce", "repro", "heuristic" → Steps / Heuristic
     - "severity", "priority", "impact" → Severity
     - "fix", "suggest", "recommendation" → Suggested Fix
     - "screenshot", "attachment", "evidence", "image" → Screenshot Ref
   - **For radio/dropdown/checkbox fields, run mapping and value-selection as a
     separate sub-step from text fields:**
     a. First map the field itself to a bug attribute using the same label logic above.
     b. Then, independently, match the bug's value for that attribute against the
        field's available `options[]` (e.g. Severity value "High" → option "High",
        or "Critical" if "High" isn't offered — pick the closest ranked equivalent).
     c. If no option is a confident match for the bug's value, leave the field
        unselected rather than guessing — add it to `unmapped_field_values`.
   - Only accept a mapping when the match is a clear keyword/synonym hit. Do not
     force a bug attribute into a field whose label doesn't clearly relate to it.
   - Track two lists:
     - `unmapped_fields`: discovered form fields with no confident matching bug attribute.
     - `unmapped_attributes`: bug attributes with no confident matching form field.
6. **Confirm mapping with the user before first use on a new form:**
   - Present the proposed `field → attribute` map (and any `unmapped_fields` /
     `unmapped_attributes` / `unmapped_field_values`) in chat.
   - Ask: *"This is my best mapping for this form. Confirm, or tell me the correct
     mapping for anything I got wrong or left blank."*
   - Apply any corrections the user gives.
   - Save the confirmed mapping to `--mapping-cache-file`, keyed by form URL/label-hash,
     so subsequent bugs (and future runs) reuse it without asking again.
7. **Content Formatting** (before filling any field):
    - Bug data in `<LOG_FILE>` is stored as raw Markdown table cells with `<br>` tags,
      pipe separators, `**bold**` markers, and inline image links.
    - **Never paste raw Markdown into form fields.** Always reformat into clean,
      human-readable plain text:
      - Replace `<br>` with line breaks.
      - Remove Markdown syntax (`**`, `![](...)`, `|`, backticks).
      - Convert numbered reproduction steps from inline `<br>`-separated text into
        actual numbered lines.
      - Structure the output with clear section headers (e.g., "Description:",
        "Steps to Reproduce:", "Suggested Fix:") so the form response reads like
        a professional bug report, not a raw data dump.
    - Example transformation:
      - **Raw log cell:** `1. Login as admin.<br>2. Navigate to Events Management.<br>3. Click the funnel icon.`
      - **Formatted for form:**
        ```
        Steps to Reproduce:
        1. Login as admin.
        2. Navigate to Events Management.
        3. Click the funnel icon.
        ```
8. Fill only the confidently-matched (or user-confirmed) fields using the appropriate
    browser tool per field type (`browser_type` for text, `browser_select_option` for
    dropdowns, `browser_click` for radio/checkbox).
9. **DO NOT CLICK SUBMIT.**
10. Present Human Review Gate in chat:
   > *"Form pre-filled in Tab **[Tab ID]** for **[Bug ID]**.*
   > *Unmapped fields (left blank): [list].*
   > *Unmapped bug attributes (not placed): [list].*
   > *Please review and manually click Submit."*

### Option B: `jira` / `slack` / `github_issues`
1. Draft the payload/issue description formatted per channel specs.
2. Display payload in chat for user confirmation.
3. Upon user approval, invoke the appropriate API/MCP tool to send the report.

## Step 3 — Post-Submission Sync & Tab Cleanup
When user confirms submission for a bug (e.g., types *"Submitted [Bug ID]"* or confirms in chat):
1. Get current local timestamp (`YYYY-MM-DD HH:mm:ss`).
2. Update the bug entry in `<LOG_FILE>` with:
   - `Submission Status`: `SUBMITTED`
   - `Submitted Channel`: `<CHANNEL_TYPE>` (`<CHANNEL_TARGET>`)
   - `Form-submission timestamp`: `<TIMESTAMP>`
3. If using `web_form`, close the associated browser tab to keep workspace clean.
4. Loop to the next bug until queue is empty.

## Non-Negotiable Rules
- Never auto-submit web forms without human confirmation.
- Never guess a field mapping without a clear keyword/synonym match — leave ambiguous
  fields blank and surface them for human review instead.
- Always check submission status in `<LOG_FILE>` prior to sending.
- Isolate browser contexts (open new tabs) for web form submissions.
- Always confirm a new form's field mapping with the user once, then cache it —
  never re-ask for a form already confirmed unless its discovered fields changed.
- **Language Preservation:** Always use the exact language found in `<LOG_FILE>` entries.
  Do not translate, paraphrase into another language, or convert between English and
  Vietnamese (or any other language). If the log is written in English, the form
  submission must remain in English — and vice versa.
- **No Raw Markdown in Forms:** Never paste raw Markdown syntax (pipes, bold markers,
  `<br>` tags, image links) into form text fields. Always reformat into clean,
  structured plain text before filling (see Step 2 → Option A → step 7).