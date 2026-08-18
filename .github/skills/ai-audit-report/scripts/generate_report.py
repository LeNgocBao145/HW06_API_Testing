import os
import sys
import re

def find_workspace_root():
    """Find the workspace root by looking for .github folder or using current directory."""
    current_path = os.getcwd()
    
    # Check if .github exists in current directory
    if os.path.exists(os.path.join(current_path, ".github")):
        return current_path
    
    # Walk up the directory tree looking for .github folder
    while current_path != os.path.dirname(current_path):
        if os.path.exists(os.path.join(current_path, ".github")):
            return current_path
        current_path = os.path.dirname(current_path)
    
    # If not found, return current working directory
    return os.getcwd()

def find_required_files(workspace_root):
    """Automatically find prompt_logs.md and the report output path."""
    log_file_path = None
    existing_report_path = None
    
    # Search for prompt_logs.md and any existing report file
    for root, dirs, files in os.walk(workspace_root):
        if "prompt_logs.md" in files and not log_file_path:
            log_file_path = os.path.join(root, "prompt_logs.md")
        if "AI_Audit_Report.md" in files and not existing_report_path:
            existing_report_path = os.path.join(root, "AI_Audit_Report.md")
    
    if not log_file_path:
        log_file_path = os.path.join(workspace_root, "prompt_logs.md")

    report_file_path = os.path.join(workspace_root, "agent_artifacts", "ai-audit-report", "AI_Audit_Report.md")
    return log_file_path, report_file_path, existing_report_path

def append_new_audit_logs(log_file_path, report_file_path, existing_report_path=None):
    # 1. Check if the source log file exists
    if not os.path.exists(log_file_path):
        print(f"File {log_file_path} not found!")
        return

    with open(log_file_path, "r", encoding="utf-8") as f:
        log_content = f.read().strip()

    if not log_content:
        # If log is empty and report doesn't exist, create an empty file
        if not os.path.exists(report_file_path):
            with open(report_file_path, "w", encoding="utf-8") as f:
                f.write("I do not use any AI help in this exercise.\n")
        print(f"File {log_file_path} is empty. Nothing to update.")
        return

    # 2. Read existing report content and preserve header and footer
    current_interactions = 0
    output_dir = os.path.dirname(report_file_path)
    os.makedirs(output_dir, exist_ok=True)

    file_exists = os.path.exists(report_file_path)
    read_report_path = report_file_path
    if not file_exists and existing_report_path and os.path.exists(existing_report_path):
        read_report_path = existing_report_path
        file_exists = True

    header_content = ""
    existing_interactions_content = ""
    footer_content = ""
    
    if file_exists:
        with open(read_report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
            
            # Find the position where interactions start
            match_start = re.search(r"(I use AI tools for the following tasks:)", report_content)
            if match_start:
                # Preserve everything before "I use AI tools..."
                header_content = report_content[:match_start.start()]
                
                # Find where interactions end (look for any ## heading that comes after interactions)
                # This will match any section like ## Signature, ## References, ## Notes, etc.
                remaining_content = report_content[match_start.end():]
                match_end = re.search(r"\n(## [^\n]+)", remaining_content)
                if match_end:
                    # There's a footer section (any ## heading)
                    interactions_end_pos = match_end.start()
                    existing_interactions_content = remaining_content[:interactions_end_pos]
                    footer_content = remaining_content[interactions_end_pos:]
                else:
                    # No footer, all content after marker is interactions
                    existing_interactions_content = remaining_content
            else:
                # No interactions marker found, preserve entire file as header
                header_content = report_content
            
            # Count the number of "### Interaction " strings already in the file
            current_interactions = len(re.findall(r"### Interaction \d+", report_content))
            
            # If the file previously had "I do not use any AI help...", remove it to write new logs
            if "I do not use any AI help in this exercise." in report_content:
                current_interactions = 0

    # 3. Scan all sessions in the log file using Regex
    session_pattern = r"### \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?::\d{2})?\]\s*-\s*([^\n]+)"
    matches = list(re.finditer(session_pattern, log_content))
    
    if not matches:
        print(f"No interactions found in the correct format in {log_file_path}!")
        return

    # 4. Filter structure: Only get sessions beyond the current count
    total_logs_in_source = len(matches)
    new_sessions_to_process = matches[current_interactions:]

    if not new_sessions_to_process:
        print(f"Synchronization complete! Report file already has {current_interactions}/{total_logs_in_source} interactions. No new logs added.")
        return

    # 5. Prepare to write file
    new_report_lines = []
    
    # We will always use write mode and reconstruct the full file
    open_mode = "w"

    # Process only new sessions
    for i, match in enumerate(new_sessions_to_process):
        # Interaction number will continue increasing from the old count
        interaction_num = current_interactions + i + 1
        timestamp = match.group(1)
        ai_tool = match.group(2).strip()
        
        # Get the body content of this new session
        # Calculate the actual position in the overall log string
        actual_index = current_interactions + i
        start_pos = match.end()
        end_pos = matches[actual_index + 1].start() if actual_index + 1 < len(matches) else len(log_content)
        session_body = log_content[start_pos:end_pos].strip()
        
        # Extract Prompt and Response
        prompt_match = re.search(r"\*\*User Prompt:\*\*\s*\n(.*?)(?=\*\*AI Response:\*\*|$)", session_body, re.DOTALL)
        response_match = re.search(r"\*\*AI Response:\*\*\s*\n(.*)", session_body, re.DOTALL)
        
        user_prompt = prompt_match.group(1).strip() if prompt_match else "> (Prompt content not found)"
        ai_output = response_match.group(1).strip() if response_match else "> (Response content not found)"

        # Create block according to standard structure
        new_report_lines.append(f"### Interaction {interaction_num}")
        new_report_lines.append(f"* **Name of the AI tool**: {ai_tool}")
        new_report_lines.append(f"* **Date and time**: {timestamp}")
        new_report_lines.append(f"* **My prompt**: \n{user_prompt}")
        new_report_lines.append(f"* **The AI output**: \n{ai_output}\n")

    # 6. Reconstruct the entire file with header + old interactions + new interactions + footer
    with open(report_file_path, open_mode, encoding="utf-8") as f:
        # Write preserved header
        if header_content:
            f.write(header_content)
        
        # Write the marker line if this is the first interaction section
        if current_interactions == 0:
            f.write("I use AI tools for the following tasks:\n\n")
        
        # Write existing interactions
        if existing_interactions_content and current_interactions > 0:
            f.write(existing_interactions_content)
            if not existing_interactions_content.endswith("\n"):
                f.write("\n")
        
        # Write new interactions
        f.write("\n".join(new_report_lines))
        
        # Write preserved footer
        if footer_content:
            if not footer_content.startswith("\n"):
                f.write("\n")
            f.write(footer_content)
        
    print(f"Successfully detected and added {len(new_sessions_to_process)} new interactions to {report_file_path}!")

if __name__ == "__main__":
    # Auto-detect workspace root and required files
    workspace_root = find_workspace_root()
    log_file_path, report_file_path, existing_report_path = find_required_files(workspace_root)
    
    print(f"Workspace root: {workspace_root}")
    print(f"Log file: {log_file_path}")
    print(f"Report file: {report_file_path}")
    
    append_new_audit_logs(log_file_path, report_file_path, existing_report_path)