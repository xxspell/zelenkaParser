import time
from bs4 import BeautifulSoup
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import settings

import structlog

logger = structlog.get_logger(__name__)


class WebPage:
    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={settings.SELENIUM_PROFILE_PATH}")
        self.driver = uc.Chrome(options=options)
        self.url = None

    def load_page(self, url):
        self.url = url
        self.driver.get(url)

    def authorize_user(self, max_attempts=3):
        for attempt in range(1, max_attempts + 1):
            nickname = self.get_username()
            if nickname:
                message = "User is authorized for user {}".format(nickname)
                logger.info(message)
                return True, nickname, message
            else:
                click, click_message = self.click_button(
                    '//a[contains(@class, "login-and-signup-btn") and contains(@href, "login/")]')
                if click:
                    logger.debug(click_message)
                    input("Log in to the site and press ENTER")
                else:
                    logger.warning(click_message)
        else:
            message = "Max attempts authorize user reached. Action could not be completed."
            logger.warning(message)
            return True, None, message
    def find_error_text(self, xpath, target_text):
        try:
            found_element = self.driver.find_element(By.XPATH, xpath)
            found_text = found_element.text
            if target_text in found_text:
                print(f"Text '{target_text}' found on the page by the specified XPath.")
                return True
            else:
                print(f"Text '{target_text}' not found on the page by the specified XPath.")
                return False
        except Exception as e:
            logger.warning('Find error text exception occurred: {}'.format(e))
            return False
    def get_comment_hide_text(self, comment_id):
        try:

            comment_id_to_extract = f"post-comment-{comment_id}"

            # Find all comments with the class "comment"
            comments = self.driver.find_elements(By.CLASS_NAME, 'comment')

            # Loop through comments to find the desired one
            for comment in comments:
                comment_id = comment.get_attribute('id')

                if comment_id == comment_id_to_extract:
                    # Extract HTML content of the desired comment
                    comment_html = comment.get_attribute('outerHTML')

                    # Use BeautifulSoup to parse the HTML and extract the text content
                    soup = BeautifulSoup(comment_html, 'html.parser')
                    quote_div = soup.find('div', class_='quote')
                    quote_text = ' '.join(quote_div.stripped_strings)

                    # Print or use the extracted text content as needed
                    message = "Successfully extracted comment hide text"
                    logger.info(message)
                    return quote_text, message
        except Exception as error:
            logger.warning('Error while parsing comment', error=str(error))
            return None, error

    def get_username(self):
        try:
            username_element = self.wait_for_element_visibility((By.ID, "NavigationAccountUsername"))
            username = username_element.text
            return username
        except (TimeoutException, NoSuchElementException):
            return None

    def click_button(self, xpath):
        try:
            button_element = self.wait_for_element_visibility((By.XPATH, xpath))
            button_element.click()
            message = "Button clicked. Text:", button_element.text
            logger.info(message)
            return True, message

        except (TimeoutException, NoSuchElementException):
            message = "Button not found or not visible on the page"
            logger.warning(message)
            return False, message

    def wait_for_element_visibility(self, locator, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def close_browser(self):
        self.driver.quit()

def rr(post_id, post_comment_id):
    try:
        url = f"https://{settings.BASE_URL}/posts/{post_id}/"

        web_page = WebPage(url)
        web_page.load_page()

        # Получить никreturn True, nickname, message
        is_authorized = web_page.authorize_user()
        if web_page.find_error_text("//div[@class='errorOverlay']//span[contains(text(), 'Запрашиваемое сообщение не найдено.')]", "Запрашиваемое сообщение не найдено."):
            if is_authorized:
                # 16547219
                hide_text, hide_text_message = web_page.get_comment_hide_text(post_comment_id)
                if hide_text is not None:
                    logger.info("Hide text:{}".format(hide_text), hide_text=hide_text)
                else:
                    logger.warning(hide_text_message)
            else:
                logger.error('User not authorized - exit')
        else:
            logger.warning("Failed get post - not found")




        time.sleep(1000)
    finally:
        web_page.close_browser()
