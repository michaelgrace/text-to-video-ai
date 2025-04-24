import json
import ast
import re

def verticalize_log(log):
    def verticalize_line(line):
        # Try to parse as JSON
        try:
            obj = json.loads(line)
            return json.dumps(obj, indent=2)
        except Exception:
            pass
        # Try to parse as Python list/dict
        try:
            obj = ast.literal_eval(line)
            return json.dumps(obj, indent=2)
        except Exception:
            pass
        # Try known patterns (timed_captions, background_video_urls, etc)
        # ...reuse your pretty_json_or_text logic here...
        return line

    for entry in log:
        entry['line'] = verticalize_line(entry['line'])
    return log

# Usage:
# with open("your_log.json") as f:
#     data = json.load(f)
# data['log'] = verticalize_log(data['log'])
# print(json.dumps(data, indent=2))
