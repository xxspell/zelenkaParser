import asyncio
import itertools
import json
import time
import traceback

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import settings
from core.api import AsyncProxyManagerAPI
from core.db import AsyncSQLiteDB
from core.utils import convert_row_to_dict, extract_information, write_to_file
import structlog

logger = structlog.get_logger(__name__)


class WebPage:
    def __init__(self):
        self.i = "[Browser]"
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={settings.SELENIUM_PROFILE_PATH}")
        self.driver = uc.Chrome(options=options)
        self.url = None

    def load_page(self, url):
        logger.debug(f"{self.i} Loading page: {url}")
        self.url = url
        self.driver.get(self.url)

    def authorize_user(self, max_attempts=3):
        for attempt in range(1, max_attempts + 1):
            nickname = self.get_username()
            if nickname:
                message = f"{self.i} User is authorized for user {nickname}"
                logger.info(message)
                return True, nickname, message
            else:
                click, click_message = self.click_button(
                    '//a[contains(@class, "login-and-signup-btn") and contains(@href, "login/")]'
                )
                if click:
                    logger.debug(click_message)
                    input(f"{self.i} Log in to the site and press ENTER")
                else:
                    logger.warning(click_message)
        else:
            message = (
                f"{self.i} Max attempts authorize user reached. Action could not be completed."
            )
            logger.warning(message)
            return True, None, message

    def find_error_text(self, xpath, target_text):
        try:
            found_element = self.driver.find_element(By.XPATH, xpath)
            found_text = found_element.text
            if target_text in found_text:
                logger.info(f"{self.i} Text '{target_text}' found on the page by the specified XPath.")
                return True
            else:
                logger.info(
                    f"{self.i} Text '{target_text}' not found on the page by the specified XPath."
                )
                return False
        except Exception as e:
            logger.warning(f"{self.i} Find error text exception occurred: {e}")
            return False

    def get_comment_hide_text(self, comment_id):
        try:
            comment_id_to_extract = f"post-comment-{comment_id}"

            # Find all comments with the class "comment"
            comments = self.driver.find_elements(By.CLASS_NAME, "comment")

            # Loop through comments to find the desired one
            for comment in comments:
                comment_id = comment.get_attribute("id")

                if comment_id == comment_id_to_extract:
                    # Extract HTML content of the desired comment
                    comment_html = comment.get_attribute("outerHTML")

                    # Use BeautifulSoup to parse the HTML and extract the text content
                    soup = BeautifulSoup(comment_html, "html.parser")
                    quote_div = soup.find("div", class_="quote")
                    quote_text = " ".join(quote_div.stripped_strings)

                    # Print or use the extracted text content as needed
                    message = f"{self.i} Successfully extracted comment hide text"
                    logger.info(message)
                    return quote_text, message
        except Exception as error:
            logger.warning(f"{self.i} Error while parsing comment", error=str(error))
            return None, error

    def bot_check_bypass(self):
        return self.click_button("//button[contains(text(), 'Я не робот')]")

    def get_username(self):
        try:
            username_element = self.wait_for_element_visibility(
                (By.ID, "NavigationAccountUsername")
            )
            username = username_element.text
            return username
        except (TimeoutException, NoSuchElementException):
            return None

    def click_button(self, xpath):
        try:
            button_element = self.wait_for_element_visibility((By.XPATH, xpath))
            button_element.click()
            message = f"{self.i} Button clicked. Text:", button_element.text
            logger.info(message)
            time.sleep(5)
            return True, message

        except (TimeoutException, NoSuchElementException):
            message = f"{self.i} Button not found or not visible on the page"
            logger.debug(message)
            return False, message

        except (StaleElementReferenceException):
            pass

    def wait_for_element_visibility(self, locator, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def close_browser(self):
        self.driver.quit()


async def get_unchecked_comments():
    db = AsyncSQLiteDB()

    # Connecting to the database
    await db.connect()
    select_data_query = "SELECT * FROM comments WHERE checked = 0;"
    data = await db.fetch_all(select_data_query)
    await db.disconnect()
    return data


async def update_table(update_values, row_id):
    db = AsyncSQLiteDB()
    await db.connect()

    # Update the record in the "comments" table by id
    await db.update_row_by_id("comments", update_values, row_id)


async def main(threads_to_parse):
    tasks = []
    for index, thread_data in enumerate(threads_to_parse, start=1):
        logger.debug(f"Processing browser_interaction task - {index}", )

        task = asyncio.create_task(while_run(index, thread_data))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def while_run(index, thread_data):
    counter = itertools.count()
    while_count = next(counter)
    while True:
        while_count = next(counter)
        loop = asyncio.get_running_loop()
        unchecked_comments = await get_unchecked_comments()
        if unchecked_comments:
            await loop.run_in_executor(None, run, index, while_count, thread_data, unchecked_comments)
        else:
            logger.info('[Browser] Queue is empty, waiting 2k seconds', while_count=while_count,
                        thread_data=thread_data, unchecked_comments=unchecked_comments)
        await asyncio.sleep(2000)


def run(index, while_count, thread_data, unchecked_comments):
    i = rf"[Browser][{index}\{while_count}]"
    poster_username = thread_data["poster_username"]
    thread_id = thread_data["thread_id"]
    extraction_rules = thread_data["extraction_rules"]
    message = thread_data["message"]
    proxy_type = thread_data["proxy_type"]
    result = unchecked_comments
    logger.info(f'{i} Get unchecked comments', result=result)
    if result:
        web_page = WebPage()
    else:
        return None, "No comments found"
    try:

        for row in result:  # TODO: Add support to distinguish which record in the database belongs to which setting
            result_dict = convert_row_to_dict(row)
            logger.debug(f"{i} Convert row to dict", result_dict=result_dict)
            post_id = result_dict["post_id"]
            post_comment_id = result_dict["post_comment_id"]
            id_row = result_dict["id"]
            comment_author = result_dict["comment_author"]
            url = f"{settings.BASE_URL}/posts/{post_id}/"

            web_page.load_page(url)
            web_page.bot_check_bypass()
            is_authorized = web_page.authorize_user()
            if not web_page.find_error_text(
                    "//div[@class='errorOverlay']//span[contains(text(), 'Запрашиваемое сообщение не найдено.')]",
                    "Запрашиваемое сообщение не найдено.",
            ):
                if is_authorized:
                    hide_text, hide_text_message = web_page.get_comment_hide_text(
                        post_comment_id
                    )
                    if hide_text is not None:
                        logger.info(
                            f"{i} Hide text:{hide_text}", hide_text=hide_text
                        )
                        result = extract_information(hide_text, extraction_rules)
                        logger.info(f"{i} Extract information", result=result)
                        if result:
                            if "proxy_info" in result:
                                ip, port, login, password = result["proxy_info"][0]
                                logger.info(
                                    f"{i}", ip=ip, port=port, login=login, password=password
                                )
                                proxy_manager = AsyncProxyManagerAPI(
                                    settings.BASE_URL_PROXYMANAGER
                                )
                                write_to_file(f"{proxy_type}://{login}:{password}@{ip}:{port}",
                                              settings.FILENAME_TO_SAVE_PROXY)
                                result = asyncio.run(
                                    proxy_manager.add_proxy(login, password, ip, port, proxy_type))

                                logger.debug(f"{i} Proxy add result", result=result)
                                if settings.CHECK_PROXIES:
                                    result = json.loads(result)
                                    proxy_id = result["id"]
                                    result = asyncio.run(
                                        proxy_manager.check_proxy(proxy_id)
                                    )
                                    logger.debug(f"{i} Proxy init check", result=result)
                                update_values = {"checked": 1, "error": 0}
                                result = asyncio.run(update_table(update_values, id_row))
                        else:
                            logger.warning(f"{i} Failed to extract information")
                            update_values = {"checked": 1, "error": 1}
                            result = asyncio.run(update_table(update_values, id_row))

                    else:
                        logger.warning(f"{i} {hide_text_message}")

                else:
                    logger.error(f"{i} User not authorized - exit")
                    update_values = {"checked": 0, "error": 0}
                    result = asyncio.run(update_table(update_values, id_row))
            else:
                logger.warning(f"{i} Failed get post - not found")
                update_values = {"checked": 1, "error": 1}
                result = asyncio.run(update_table(update_values, id_row))

            time.sleep(100)

    except Exception as error:

        logger.error(f"{i} Error occurred: {error}")
        logger.error(traceback.format_exc())
    finally:
        web_page.close_browser()
