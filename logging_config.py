import logging
from pathlib import Path


# Find the project's main folder
PROJECT_ROOT = Path(__file__).parent

# Create the logs folder if it doesn't exist
LOGS_FOLDER = PROJECT_ROOT / "logs"
LOGS_FOLDER.mkdir(exist_ok=True)

# Choose where the log messages will be saved
LOG_FILE = LOGS_FOLDER / "studysync.log"


# Configure how StudySync records log messages
logging.basicConfig(
    force = True,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


# Create a logger that other files can reuse
logger = logging.getLogger("studysync")