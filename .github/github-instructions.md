# GitHub Contribution Guidelines

## Critical Guidelines

### DO NOT REMOVE Comments and Code
- **NEVER** modify code outside the scope of the current task
- **NEVER** refactor or "improve" code that works unless specifically requested
- **NEVER** delete existing functions, methods, or classes
- **NEVER** modify comments outside the scope of the current task
- **NEVER** give instructions to add code when that code is already in place
- Comments marked with "DO NOT REMOVE" are critical and must be preserved
- When modifying files, preserve all existing comments

### Code Preservation Requirements
Must preserve:
- Function signatures
- Return types
- Parameter names
- Existing behavior
- Comments containing important context
- Existing code style (tabs vs spaces, naming conventions)

### Code Modification Scope
1. Focus only on the specific task requested
2. Use `// ...existing code...` or `# ...existing code...` to indicate unchanged sections
3. When making changes, only show the specific parts that need to be modified
4. Do NOT change any function signatures

## Technical Standards

### Build and Performance
- Keep dependencies in separate layers for better Docker caching
- Preserve pip cache between builds for faster installation
- Use multi-stage builds when appropriate
- Test changes locally before pushing

### Directory Structure
- Maintain the existing directory structure:
  - `/output` - Generated files
  - `/temp` - Temporary processing files
  - `/utility` - Core functionality
  - `/.logs` - API response logs

### Style Guidelines
- Follow PEP 8 for Python code
- Keep line lengths under 88 characters
- Include descriptive comments for complex logic
- Match existing code style

## Documentation and Process

### Code Organization
- Show file path at the beginning of each code block: `// filepath: path/to/file.py`
- Focus only on the specific task requested
- If multiple files need changes, clearly separate them with headings
- If the solution seems incomplete, ASK before making assumptions

### Pull Request Format
1. Start with a brief explanation of your approach
2. Document what will NOT be changed
3. Show code changes with proper file headers and minimal context
4. End with instructions on how to test the changes
5. If there are multiple approaches possible, ASK before implementing
6. Test with Docker builds

## Why These Guidelines Matter

These instructions exist to:
- Maintain codebase stability
- Preserve institutional knowledge in comments
- Prevent unintended side effects
- Keep build times optimal
- Ensure consistent behavior across all contributors

Remember: When in doubt, ask before modifying or removing any existing code or comments.
