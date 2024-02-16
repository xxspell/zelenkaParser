# parser.py
import asyncio
import time
import argparse
import traceback

import settings

from core.api_interaction import main as api_integration
from core.browser_interaction import main as browser_integration
import structlog

logger = structlog.get_logger(__name__)


async def parse_title(param1, param2):
    await asyncio.sleep(2)
    print(f"Title ({param1}, {param2})")


async def launch_browser_interaction(pause_duration, repeat_interval, threads_to_parse):
    logger.info("Run browser integration",
                config=threads_to_parse)
    try:
        await browser_integration(threads_to_parse)
    except Exception as e:
        logger.error("Error in browser interation", error=e, traceback=traceback.format_exc())


async def launch_api_interaction(pause_duration, repeat_interval, threads_to_parse):
    logger.info("Run api integration", pause_duration=pause_duration, repeat_interval=repeat_interval,
                config=threads_to_parse)
    try:
        await api_integration(pause_duration, repeat_interval, threads_to_parse)
    except Exception as e:
        logger.error("Error in api interation", error=e, traceback=traceback.format_exc())


async def main(one_function):
    tasks = []
    for function_params in settings.TASKS:
        if one_function is not None:
            if function_params['function_name'] != one_function:
                logger.info(f"Function name not found in settings.TASKS")
                continue  # Skip the function if its name does not match the name specified by the user

        tasks = []  # List of tasks to wait for completion
        # Run the selected functions for parsing with their parameters
        function_name = function_params['function_name']
        del function_params['function_name']  # Remove the extra parameter
        function = globals()[function_name]
        task = asyncio.create_task(function(**function_params))
        logger.info(f"Running function {function_name} with parameters {function_params}")
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
