# parser.py
import asyncio
import time

import settings
from core.test import rr
from core.db import main as gg
# from core.api import main as bb

from core.api_interaction import main as api_integration
import structlog
logger = structlog.get_logger(__name__)

async def parse_title(param1, param2):
    await asyncio.sleep(2)
    print(f"Title ({param1}, {param2})")

async def parse_paragraphs(param1, param2):
    print(f"Paragraph ({param1}, {param2}")


async def launch_api_interation(pause_duration, repeat_interval, threads_to_parse):
    logger.info("Run api integration", pause_duration=pause_duration, repeat_interval=repeat_interval)
    while True:
        try:
            api_integration()



# Другие функции для парсинга

async def main():
    # Запускаем выбранные функции для парсинга с их параметрами
    tasks = []
    for function_params in settings.TASKS:
        function_name = function_params['function_name']
        del function_params['function_name']  # Удаляем лишний параметр
        function = globals()[function_name]
        task = asyncio.create_task(function(**function_params))
        tasks.append(task)

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

# if __name__ == "__main__":
#     # rr()
#
#
#     # asyncio.run(gg())
#     asyncio.run(bb(12, '+'))