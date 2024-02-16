import logging
import os

import structlog

from dotenv import load_dotenv


load_dotenv()

DOMAIN = "zelenka.guru"
BASE_URL = f"https://{DOMAIN}"

API_URL = f"https://api.{DOMAIN}"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(BASE_DIR, "data", "database.db")
# Define the path to the profile folder inside the data folder
SELENIUM_PROFILE_PATH = os.path.join(BASE_DIR, "data", "browser_profile")

FILENAME_TO_SAVE_PROXY = os.path.join(BASE_DIR, "data", "proxy.txt")
THREADS_TO_PARSE = [
    {
        "poster_username": "h0ppy",
        "thread_id": "5249550",
        "extraction_rules": [('proxy_info', r'(\d+\.\d+\.\d+\.\d+):(\d+):(\w+):(\w+)')],
        "message": "+",
        "proxy_type": "http"
    },
    # {extract_information("KitagawaMarin , Спонсор раздачи ЛУЧШИЙ магазин прокси zelenka.guru/threads/3771847/ ------ ТВОЯ ПРОКСИ:   163.5.60.163:5771:user154390:kt4g57", )
    #     'poster_username': 'h0ppy',
    #     'thread_id': 'value1',
    #     'extraction_rules': [
    #         ('proxy_info', r'(\d+\.\d+\.\d+\.\d+) :(\d+):(\w+):(\w+)')
    #     ],
    # },и
]

# Specifying functions to run
TASKS = [
    # {
    #     'function_name': 'selenium_parse',
    #     'param1': 'value1',
    #     'param2': 'value2',
    # },
    {
        "function_name": "launch_api_interaction",
        "pause_duration": "70 150",
        "repeat_interval": "1600 2300",
        "threads_to_parse": THREADS_TO_PARSE,
    },
    {
        "function_name": "launch_browser_interaction",
        "pause_duration": "70 150",
        "repeat_interval": "1600 2300",
        "threads_to_parse": THREADS_TO_PARSE,
    },
]

MAX_PARALLEL_REQUESTS = 5
TIMEOUT_SECONDS = 10

DB_USERFIELDS = [
    ("id", "INTEGER PRIMARY KEY"),
    ("post_comment_id", "INTEGER"),
    ("post_id", "INTEGER"),
    ("comment_hide_text", "TEXT"),
    ("comment_author", "TEXT"),
    ("date_add", "TEXT"),
    ("checked", "INTEGER"),
    ("error", "INTEGER"),
]


BASE_URL_PROXYMANAGER = "https://shawty.fun"
CHECK_PROXIES = True


structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False
)

logger = structlog.get_logger(__name__)