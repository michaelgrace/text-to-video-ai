# Development Environment Configuration

## Hardware/Software Requirements

### My Local System Specifications
- Windows 11 Pro
- 32GB RAM
- Dual GPU Setup:
- Intel UHD Graphics (integrated, shared memory) - Use this GPU for app 
  - NVIDIA Quadro P1000 (4GB dedicated)
- Docker Desktop with WSL2
- No local Python installation required (handled by Docker)

### Build Time Considerations
- Initial build time: ~15-20 minutes
- Subsequent builds with cache: ~5-10 minutes
- Video generation time: ~2-4 minutes per minute of output
- Hardware acceleration using Intel GPU via VAAPI

### Performance Notes
- Docker memory allocation critical for build performance
- FFmpeg uses Intel QuickSync via VAAPI
- Temporary files managed through volume mounts
- Build caching optimized through:
  - pip cache persistence
  - BuildKit layers
  - Proper dependency ordering

### GPU Configuration Notes
- Intel GPU support:
  - Uses VAAPI for hardware acceleration
  - Requires intel-media-va-driver-non-free
  - Configured through docker-compose devices mount
  - Environment variables for VAAPI configuration

### Docker Configuration
- BuildKit enabled
- Volume mounts for:
  - Source code
  - Output files
  - Temporary files
  - pip cache
- GPU device pass-through configured

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

### Code Formatting Standards
1. Code Changes Format:
   - Always use `// ...existing code...` or `# ...existing code...` (language dependent) to indicate unchanged sections
   - Keep changes concise and focused
   - Show only the minimal context needed to understand the change

2. Multiple Changes in Same File:
   - Use a single code block per file
   - Show changes in their correct relative positions
   - Maintain proper context with existing code markers

3. Filepath Conventions:
   - Include exact filepath as a comment at the start of every code block
   - Preserve original slash style (forward or backward)
   - Format: `// filepath: d:\path\to\file.ext`

Example of proper code block formatting:
```python
# filepath: d:\path\to\example.py
# ...existing code...
def process_video(input_file, output_file, quality=HIGH_QUALITY):
    """Process video with specified quality"""
    # ...existing code...
```

### Build and Performance
- Keep dependencies in separate layers for better Docker caching
- Preserve pip cache between builds for faster installation
- Use multi-stage builds when appropriate
- Test changes locally before pushing

### Directory Structure
- Maintain the existing directory structure:
  - `/exports` - Generated files
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
