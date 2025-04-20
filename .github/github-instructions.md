# Development Environment Configuration

## Hardware/Software Requirements

### System Specifications
- Windows 11 Pro 32GB RAM
- Dual GPU Setup:
  - Intel UHD Graphics (integrated, shared memory)
  - NVIDIA Quadro P1000 (4GB dedicated)
- Docker Desktop with WSL2
- No local Python installation required (handled by Docker)

### Build Time Considerations
- Initial build time: ~15-20 minutes
- Subsequent builds with cache: ~5-10 minutes
- Video generation time: ~2-4 minutes per minute of output
- Hardware acceleration using Intel UHD preferred over NVIDIA due to memory management

### Performance Notes
- Docker memory allocation critical for build performance
- FFmpeg uses Intel QuickSync via VAAPI
- Temporary files managed through volume mounts
- Video processing benefits from shared system memory with integrated GPU

### GPU Configuration Notes
- Primary GPU: Intel UHD
  - Preferred for this project
  - Better memory management with shared RAM
  - Avoids dedicated VRAM limitations
- Secondary GPU: NVIDIA Quadro P1000
  - Available but not primary for video processing
  - 4GB VRAM limitation can cause issues

### Docker Desktop Configuration
- WSL2 backend required
- Recommended memory allocation: 16GB
- GPU access enabled through Docker Desktop settings

# GitHub Contribution Guidelines

## Critical Guidelines

### GITHUB CHECKINS
- **NEVER** suggest any code that will delete my current files
- **ALWAYS** prompt for local backup before git operations
- **VERIFY** .gitignore isn't excluding critical folders
- **CHECK** working directory before stash operations
- **CONFIRM** files are tracked before commits

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

### Git Commit Process
When clicking the COMMIT button in your IDE:
1. Local Changes:
   - Staged changes are committed to your local repository
   - A commit hash is generated
   - Your local branch is updated

2. Remote Sync Required:
   - Changes are NOT automatically pushed to remote
   - You must explicitly PUSH to sync with remote:
     ```bash
     git push origin <branch-name>
     ```
   - Or use your IDE's "Push" button/command

3. Best Practices:
   - Write clear commit messages
   - Pull before pushing to avoid conflicts
   - Verify changes are pushed using GitHub web interface

## Why These Guidelines Matter

These instructions exist to:
- Maintain codebase stability
- Preserve institutional knowledge in comments
- Prevent unintended side effects
- Keep build times optimal
- Ensure consistent behavior across all contributors

Remember: When in doubt, ask before modifying or removing any existing code or comments.
