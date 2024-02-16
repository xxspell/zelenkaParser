import asyncio

import settings
from core.api import AsyncLolzAPI
import structlog
import random
import itertools
from core.db import AsyncSQLiteDB

logger = structlog.get_logger(__name__)


async def main(pause_duration, repeat_interval, threads_to_parse):
    tasks = []
    for index, thread_data in enumerate(threads_to_parse, start=1):
        logger.debug(f"Processing api_interaction task - {index}", )

        task = asyncio.create_task(while_run(index, pause_duration, repeat_interval, thread_data))
        tasks.append(task)
    await asyncio.gather(*tasks)

async def while_run(index, pause_duration, repeat_interval, thread_data):
    counter = itertools.count()
    while_count = next(counter)
    while True:
        while_count = next(counter)
        await run(index, while_count, pause_duration, repeat_interval, thread_data)

async def run(index, while_count, pause_duration, repeat_interval, thread_data, max_length=30):
    i = rf"[Api][{index}\{while_count}]"
    poster_username = thread_data["poster_username"]
    thread_id = thread_data["thread_id"]
    extraction_rules = thread_data["extraction_rules"]
    message = thread_data["message"]
    pause_start, pause_end = map(int, pause_duration.split(' '))
    repeat_start, repeat_end = map(int, repeat_interval.split(' '))

    logger.info(f"{i} Start write comment, and wait comment topic starter", poster_username=poster_username,
                thread_id=thread_id, extraction_rules=extraction_rules, message=message)

    base_url = settings.API_URL
    access_token = settings.ACCESS_TOKEN

    async_api = AsyncLolzAPI(base_url, access_token)

    thread_info, status = await async_api.get_thread(thread_id)
    if "Запрашиваемая тема не найдена" in thread_info:
        logger.warning(f"{i} Thread not found", thread_info=thread_info)
    else:
        logger.info(f"{i} Thread found", thread_info=str(thread_info)[:max_length])

        await sleep(pause_start, pause_end, 0.2, i, "to write a post",
                    thread_info=str(thread_info)[:max_length])

        new_post, status = await async_api.create_post(thread_id, message)
        if "error" in new_post:
            logger.warning(f"{i} Error in post creation", new_post=new_post)
        else:
            post_id = new_post["post"]["post_id"]

            logger.info(f"{i} Post created", post_id=post_id, new_post=str(new_post)[:max_length])
            while True:

                await sleep(pause_start, pause_end, 1, i, "to get a comment on a post",
                            post_id=post_id)

                post_comments, status = await async_api.get_post_comments(post_id)
                if "Запрашиваемое сообщение не найдено" in post_comments:
                    logger.info(f"{i} Desired comment not found, repeat", post_id=post_id, new_post=str(new_post)[:max_length])
                    pass
                else:
                    for comment in post_comments.get("comments", []):
                        if comment.get("poster_username") == poster_username:

                            post_comment_id = comment.get("post_comment_id")
                            post_id = comment.get("post_id")

                            logger.info(f"{i} Found the right comment", post_id=post_id,
                                        post_comment_id=post_comment_id)

                            db = AsyncSQLiteDB()

                            try:
                                logger.debug(f"{i} Starting database connection")
                                await db.connect()
                                logger.debug(f"{i} Database connection established")

                                logger.debug(f"{i} Inserting comment into database")
                                await db.insert_comment(
                                    "comments",
                                    post_comment_id=post_comment_id,
                                    post_id=post_id,
                                    comment_author=poster_username,
                                    checked=0,
                                    error=0,
                                )
                            except ConnectionError as conn_err:
                                logger.error(f"{i} Connection error while connecting to the database", error=conn_err)
                                try:
                                    await db.connect()
                                except ConnectionError as recon_err:
                                    logger.error(f"{i} Failed to reconnect to the database", error=recon_err)
                            else:

                                logger.debug(f"{i} Comment inserted to db successfully")

                            finally:

                                await db.disconnect()
                                break
                        else:
                            logger.info(f"{i} Desired comment not found, repeat", post_id=post_id, new_post=str(new_post)[:max_length])
                            pass


                    await sleep(repeat_start, repeat_end, 1, i, "to repeat task",
                                thread_id=thread_id)
                    break


async def sleep(start, end, multiplier, i, message_text, **kwargs):
    time_to_sleep = random.uniform(start, end) * multiplier
    logger.info(f"{i} Sleep {message_text} seconds {time_to_sleep}", **kwargs)
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep
