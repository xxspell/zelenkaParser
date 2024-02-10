# parser.py
import asyncio
import time
import argparse
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


async def launch_api_interaction(pause_duration, repeat_interval, threads_to_parse):
    logger.info("Run api integration", pause_duration=pause_duration, repeat_interval=repeat_interval, config=threads_to_parse)
    while True:
        try:
            for thread_info in threads_to_parse:
                await api_integration(pause_duration, repeat_interval, threads_to_parse)
        except Exception as e:
            logger.error("Error in api interation", error=e)



# Другие функции для парсинга

async def main(one_function):
    # Запускаем выбранные функции для парсинга с их параметрами


    tasks = []
    for function_params in settings.TASKS:
        if one_function is not None:
            if function_params['function_name'] != one_function:
                logger.info(f"Function name not found in settings.TASKS")
                continue  # Пропускаем функцию, если её имя не совпадает с именем, указанным пользователем


        tasks = []  # Список задач для ожидания их завершения
        # Запускаем выбранные функции для парсинга с их параметрами
        function_name = function_params['function_name']
        del function_params['function_name']  # Удаляем лишний параметр
        function = globals()[function_name]
        task = asyncio.create_task(function(**function_params))
        print(f"Running function {function_name} with parameters {function_params}")
        tasks.append(task)


    await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for running functions with parameters from config")
    parser.add_argument("--f", type=str, help="Name of the function to run")
    args = parser.parse_args()

    if args.f:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(args.f))

    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(None))