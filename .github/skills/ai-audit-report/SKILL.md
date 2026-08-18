---
name: ai-audit-report
description: Automatically generate or populate the AI Audit Report based on the interaction history from prompt logs.
---

# Execution Logic (File Handling):
1. Check if the file `AI_Audit_Report.md` already exists in the workspace.
2. If the file DOES NOT exist: Create a new file named `AI_Audit_Report.md`.
3. If the file EXISTS: Overwrite or append the content into the existing file as requested by the workflow, ensuring the final output matches the required format perfectly.

# Using the Script

## Automatic Path Detection
The provided Python script (`scripts/generate_report.py`) automatically detects and processes the required files:

### How Path Detection Works:
1. **Workspace Root Detection**: The script first identifies the workspace root by searching for a `.github` folder in the current directory or by walking up the directory tree.
2. **File Discovery**: Once the workspace root is found, the script searches for:
   - `prompt_logs.md` - The source file containing AI interaction logs
   - `AI_Audit_Report.md` - The output file where the audit report will be generated
3. **Default Locations**: If files are not found during the search, the script defaults to looking for them in the workspace root directory.

### Running the Script:
```bash
# Navigate to the project root or any subdirectory containing .github folder
cd /path/to/workspace

# Run the script (it will auto-detect all paths and write the report into agent_artifacts)
python .github/skills/ai-audit-report/scripts/generate_report.py
```

### Script Output:
The script will display:
- The detected workspace root path
- The full path to the `prompt_logs.md` file being processed
- The full path to the `agent_artifacts/ai-audit-report/AI_Audit_Report.md` file being created/updated
- A success message with the number of new interactions added

### What the Script Does:
1. **Incremental Updates**: Only adds new interactions that aren't already in the report
2. **State Management**: Tracks existing interactions and avoids duplicating them
3. **Automatic File Creation**: Creates `AI_Audit_Report.md` if it doesn't exist
4. **Proper Formatting**: Ensures all output follows the required Markdown format
5. **Empty State Handling**: Creates an appropriate message if no interactions are found