import json
import ast
import re
import sys
from pathlib import Path

def verticalize_log_line(line):
    # Pretty-print timed_captions: lines vertically
    if line.strip().startswith("timed_captions:"):
        match = re.search(r'timed_captions:\s*(\[.*\])', line)
        if match:
            captions_str = match.group(1)
            try:
                captions = ast.literal_eval(captions_str)
                pretty_lines = []
                for segment in captions:
                    time_range, text = segment
                    pretty_lines.append(f"  {time_range}: {text}")
                return "timed_captions:\n" + "\n".join(pretty_lines)
            except Exception:
                return line
    # Pretty-print Timed Captions:((...))((...)) lines vertically
    if line.strip().startswith("Timed Captions:"):
        matches = re.findall(r'\(\(([^,]+), ([^\)]+)\), [\'"](.+?)[\'"]\)', line)
        if matches:
            pretty_lines = []
            for start, end, text in matches:
                pretty_lines.append(f"  [{start}, {end}]: {text}")
            return "Timed Captions:\n" + "\n".join(pretty_lines)
    # Pretty-print Text ```json [ ... ] ``` lines vertically
    match = re.search(r'```json\s*(\[.*\])\s*```', line)
    if match:
        try:
            arr = ast.literal_eval(match.group(1))
            pretty_lines = []
            for segment in arr:
                if isinstance(segment, list) and len(segment) == 2:
                    time_range, keywords = segment
                    pretty_lines.append(f"  {time_range}: {keywords}")
            return "Text JSON:\n" + "\n".join(pretty_lines)
        except Exception:
            return line
    match2 = re.search(r'Text ```json\s*(\[.*\])\s*```', line)
    if match2:
        try:
            arr = ast.literal_eval(match2.group(1))
            pretty_lines = []
            for segment in arr:
                if isinstance(segment, list) and len(segment) == 2:
                    time_range, keywords = segment
                    pretty_lines.append(f"  {time_range}: {keywords}")
            return "Text JSON:\n" + "\n".join(pretty_lines)
        except Exception:
            return line
    # Pretty-print background_video_urls: lines vertically
    if line.strip().startswith("background_video_urls:"):
        match = re.search(r'background_video_urls:\s*(\[.*\])', line)
        if match:
            urls_str = match.group(1)
            try:
                arr = ast.literal_eval(urls_str)
                pretty_lines = []
                for segment in arr:
                    if isinstance(segment, list) and len(segment) == 2:
                        time_range, url = segment
                        pretty_lines.append(f"  {time_range}: {url}")
                return "background_video_urls:\n" + "\n".join(pretty_lines)
            except Exception:
                return line
    return line

def verticalize_log(log):
    for entry in log:
        if "line" in entry:
            entry["line"] = verticalize_log_line(entry["line"])
    return log

def main(input_path, output_path=None):
    input_path = Path(input_path)
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "log" in data:
        data["log"] = verticalize_log(data["log"])
    else:
        print("No 'log' key found in JSON.")
        return
    if not output_path:
        output_path = input_path.with_name(input_path.stem + "_vertical.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Verticalized log saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verticalize_log.py <input_log.json> [output_log.json]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    main(input_path, output_path)
