import os
from datetime import datetime
import json
from config.settings import settings

# Log types
LOG_TYPE_GPT = "GPT"
LOG_TYPE_PEXEL = "PEXEL"

# Log paths from settings
DIRECTORY_LOG_GPT = settings.LOG_PATHS["GPT"]
DIRECTORY_LOG_PEXEL = settings.LOG_PATHS["PEXEL"]

def log_response(log_type, query, response):
    log_entry = {
        "query": query,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    if log_type == LOG_TYPE_GPT:
        if not os.path.exists(DIRECTORY_LOG_GPT):
            os.makedirs(DIRECTORY_LOG_GPT)
        filename = settings.GPT_LOG_FILENAME_PATTERN.format(
            datetime.now().strftime(settings.DATE_FORMAT))
        filepath = os.path.join(DIRECTORY_LOG_GPT, filename)
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(log_entry) + '\n')

    if log_type == LOG_TYPE_PEXEL:
        if not os.path.exists(DIRECTORY_LOG_PEXEL):
            os.makedirs(DIRECTORY_LOG_PEXEL)
        filename = settings.PEXEL_LOG_FILENAME_PATTERN.format(
            datetime.now().strftime(settings.DATE_FORMAT))
        filepath = os.path.join(DIRECTORY_LOG_PEXEL, filename)
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(log_entry) + '\n')
