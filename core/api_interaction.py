import asyncio

import settings
from core.api import AsyncLolzAPI
import structlog

from core.db import AsyncSQLiteDB

logger = structlog.get_logger(__name__)

async def main(thread_id, message, poster_username):
    base_url = settings.API_URL
    access_token = settings.ACCESS_TOKEN

    async_api = AsyncLolzAPI(base_url, access_token)

    # Пример асинхронного запроса информации о теме
    thread_info = await async_api.get_thread(5249550)
    if "Запрашиваемая тема не найдена" in thread_info:
        logger.warning('Thread not found', thread_info=thread_info)
    else:
        logger.info('Thread found', thread_info=thread_info)
        await asyncio.sleep(5)
        new_post = await async_api.create_post(5249550, "+")
        if "error" in new_post:
            logger.warning('Error in post creation', new_post=new_post)
        else:
            post_id = new_post["post"]["post_id"]
            logger.info("Post created", post_id=post_id, new_post=new_post)
            while True:
                await asyncio.sleep(1)
                post_comments = await async_api.get_post_comments(post_id)
                if "Запрашиваемое сообщение не найдено" in post_comments:
                    pass
                else:
                    for comment in post_comments.get("comments", []):

                        if comment.get("poster_username") == poster_username:
                            post_comment_id = comment.get("post_comment_id")
                            post_id = comment.get("post_id")
                            db = AsyncSQLiteDB()

                            # Подключение к базе данных
                            await db.connect()
                            await db.insert_comment('comments', post_comment_id=post_comment_id, post_id=post_id, comment_author=poster_username, checked=0, error=0)
                            await db.disconnect()
                            break
                    break
