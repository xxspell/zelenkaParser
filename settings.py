import os

import structlog

from dotenv import load_dotenv
logger = structlog.get_logger(__name__)
load_dotenv()

DOMAIN = "zelenka.guru"
BASE_URL = f"https://{DOMAIN}"

API_URL = f"https://api.{DOMAIN}"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')
# Определите путь к папке профиля внутри папки data
SELENIUM_PROFILE_PATH = os.path.join(BASE_DIR, 'data', 'browser_profile')

URL_TO_PARSE = "https://example.com"

THREADS_TO_PARSE = [
    {
        'poster_username': 'h0ppy',
        'thread_id': '5249550',
        'extraction_rules': [
                        ('proxy_info', r'(\d+\.\d+\.\d+\.\d+) :(\d+):(\w+):(\w+)')
                        ],
    },
    # {
    #     'poster_username': 'h0ppy',
    #     'thread_id': 'value1',
    #     'extraction_rules': [
    #         ('proxy_info', r'(\d+\.\d+\.\d+\.\d+) :(\d+):(\w+):(\w+)')
    #     ],
    # },
    # Другие функции с их параметрами
]
# Указание функций для запуска
TASKS = [
    # {
    #     'function_name': 'selenium_parse',
    #     'param1': 'value1',
    #     'param2': 'value2',
    # },
    {
        'function_name': 'launch_api_interaction',
        'pause_duration': '70, 150',
        'repeat_interval': '1600 2300',
        'threads_to_parse': THREADS_TO_PARSE,
    },
    # Другие функции с их параметрами
]

# Другие настройки
MAX_PARALLEL_REQUESTS = 5
TIMEOUT_SECONDS = 10


DB_USERFIELDS = [
            ('id', 'INTEGER PRIMARY KEY'),
            ('post_comment_id', 'INTEGER'),
            ('post_id', 'INTEGER'),
            ('comment_hide_text', 'TEXT'),
            ('comment_author', 'TEXT'),
            ('date_add', 'TEXT'),
            ('checked', 'INTEGER'),
            ('error', 'INTEGER')
        ]


BASE_URL_PROXYMANAGER = "https://shawty.fun"
CHECK_PROXIES = True