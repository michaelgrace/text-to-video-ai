# AI Interaction Guide

## Key Lessons Learned

### How to Start Tasks
1. Always begin by stating:
   - What must NOT be changed
   - The specific scope of changes
   - Any critical comments that must be preserved

2. Example task start:
   ```
   Following .github/github-instructions.md:
   - DO NOT CHANGE: [list specific things]
   - SCOPE: [specific changes needed]
   - PRESERVE: All "DO NOT REMOVE" comments
   ```

### Common Pitfalls
1. **Over-optimization Issues**
   - AI tends to "improve" everything it sees
   - Always explicitly state what should NOT be changed
   - Stop AI before it shows changes if it hasn't listed constraints

2. **Breaking Working Code**
   - AI often ignores "DO NOT REMOVE" comments
   - AI tends to refactor working code unnecessarily
   - Require AI to justify each change against guidelines

3. **Time Wasters**
   - Letting AI show changes before confirming understanding
   - Not catching scope creep early
   - Not reviewing constraint understanding first

### Effective Communication Patterns

1. **Three-Step Process**
   ```
   Step 1: "List what you will NOT change"
   Step 2: "Explain your planned changes"
   Step 3: "Now show the changes"
   ```

2. **Course Correction**
   ```
   When AI deviates: "You're violating [specific guideline].
   Please list what should NOT be changed before continuing."
   ```

3. **Scope Control**
   ```
   "Focus ONLY on [specific task].
   Do not modify [specific elements]."
   ```

## Session Notes

### [Date] Docker Build Optimization Session
1. **What Worked**
   - Making AI explain constraints first
   - Stopping AI before it modified critical comments
   - Creating explicit guidelines file

2. **What Didn't Work**
   - Assuming AI would remember constraints
   - Not catching scope creep early
   - Letting AI show changes before understanding constraints

3. **Key Takeaways**
   - Always verify constraint understanding first
   - Use three-step process for changes
   - Maintain strict scope control

## Quick Reference

### Task Template
```
Following .github/github-instructions.md:
1. List what will NOT be changed
2. Explain planned changes
3. Show changes only after confirmation
```

### Correction Template
```
Stop. You're violating [guideline].
1. List what should NOT change
2. Explain why your changes are within scope
3. Confirm preservation of critical elements
```

Remember: The AI is powerful but needs consistent constraint reminders.
