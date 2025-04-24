import re
import ast

def pretty_print_timed_captions(line):
    # Extract the part after 'timed_captions: '
    match = re.search(r'timed_captions:\s*(\[.*\])', line)
    if not match:
        return line  # Return as-is if not found
    captions_str = match.group(1)
    try:
        # Convert to Python list (safe eval)
        captions = ast.literal_eval(captions_str)
        # Format each caption on its own line
        pretty_lines = []
        for segment in captions:
            time_range, text = segment
            pretty_lines.append(f"  {time_range}: {text}")
        return "timed_captions:\n" + "\n".join(pretty_lines)
    except Exception:
        return line  # Return as-is if parsing fails

# Example usage:
formatted = pretty_print_timed_captions(log_entry["line"])
print(formatted)
