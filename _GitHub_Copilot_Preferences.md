# My GitHub Copilot Preferences
"Follow the guidelines in my _GitHub_Copilot_Preferences.md document, especially the part about NEVER modifying unrelated code."

## IMPORTANT - DO NOT MODIFY UNRELATED CODE
- **NEVER** modify code outside the scope of the current task
- **NEVER** refactor or "improve" code that works unless specifically requested
- **NEVER** delete existing functions, methods, or classes
- When making changes, only show the specific parts that need to be modified
- Use `// ...existing code...` or `# ...existing code...` to indicate unchanged sections

# DIRECTIVE: PRESERVE ALL:
- Function signatures
- Return types
- Parameter names
- Existing behavior

# FIX ONLY the focused integration issue while ensuring that:
1. Do NOT change any function signatures

## Code Organization
- Show file path at the beginning of each code block: `// filepath: path/to/file.py`
- Focus only on the specific task requested
- If multiple files need changes, clearly separate them with headings
- If the solution seems incomplete, ASK before making assumptions

## Style Guidelines
- Follow PEP 8 for Python code
- Keep line lengths under 88 characters
- Include descriptive comments for complex logic
- Match the existing code style (tabs vs spaces, naming conventions)

## Response Format
- Start with a brief explanation of your approach
- Show code changes with proper file headers and minimal context
- End with instructions on how to test the changes if appropriate
- If there are multiple approaches possible, ask before implementing