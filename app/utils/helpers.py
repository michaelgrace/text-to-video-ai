import os
from datetime import datetime
import json
import glob

# Log types
LOG_TYPE_GPT = "GPT"
LOG_TYPE_PEXEL = "PEXEL"

# log directory paths
DIRECTORY_LOG_GPT = "exports/logs/gpt_logs"
DIRECTORY_LOG_PEXEL = "exports/logs/pexel_logs"

# Retain only the 100 most recent log files if enabled
def prune_pexel_logs():
    prune = str(os.environ.get("PRUNE_PEXEL_LOGS", "False")).lower() in ("true", "1", "yes")
    if not prune:
        return
    files = sorted(glob.glob(os.path.join(DIRECTORY_LOG_PEXEL, "*.jsonl")))
    if len(files) > 100:
        for f in files[:-100]:
            try:
                os.remove(f)
            except Exception:
                pass

# Helper to get the current run's log filename (timestamp + title)
def get_pexel_log_filepath(title):
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}_{safe_title}_pexel.jsonl"
    if not os.path.exists(DIRECTORY_LOG_PEXEL):
        os.makedirs(DIRECTORY_LOG_PEXEL)
    return os.path.join(DIRECTORY_LOG_PEXEL, filename)

# Store the current run's log file path and deduplication dictionary in global variables
CURRENT_PEXEL_LOG_FILE = None
PEXEL_LOG_DEDUP = {}

def start_pexel_recipe_log(title):
    global CURRENT_PEXEL_LOG_FILE, PEXEL_LOG_DEDUP
    CURRENT_PEXEL_LOG_FILE = get_pexel_log_filepath(title)
    PEXEL_LOG_DEDUP = {}
    prune_pexel_logs()

def log_response(log_type, query, response, title=None, theme=None, topic=None, sentence=None):
    global PEXEL_LOG_DEDUP, CURRENT_PEXEL_LOG_FILE
    if log_type == LOG_TYPE_GPT:
        if not os.path.exists(DIRECTORY_LOG_GPT):
            os.makedirs(DIRECTORY_LOG_GPT)
        filename = '{}_gpt3.txt'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        filepath = os.path.join(DIRECTORY_LOG_GPT, filename)
        log_entry = {
            "query": query,
            "response": response,
            "theme": theme,
            "topic": topic,
            "sentence": sentence
        }
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(log_entry, indent=2) + '\n')
    elif log_type == LOG_TYPE_PEXEL:
        key = query
        if key not in PEXEL_LOG_DEDUP:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response
            }
            PEXEL_LOG_DEDUP[key] = log_entry

def finalize_pexel_recipe_log():
    global CURRENT_PEXEL_LOG_FILE, PEXEL_LOG_DEDUP
    if CURRENT_PEXEL_LOG_FILE and PEXEL_LOG_DEDUP:
        with open(CURRENT_PEXEL_LOG_FILE, "w", encoding="utf-8") as f:
            for entry in PEXEL_LOG_DEDUP.values():
                f.write(json.dumps(entry) + '\n')
    CURRENT_PEXEL_LOG_FILE = None
    PEXEL_LOG_DEDUP = {}
