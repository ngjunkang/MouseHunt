import json
import time
import datetime
import random
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import LOGGER
from cv import read_captcha

with open("facebook_credentials.json", "r") as f:
    credentials = json.loads(f.read())
    email, password = credentials["email"], credentials["password"]

login_url = "https://www.facebook.com/login.php"
game_url = "https://apps.facebook.com/mousehunt/"
horn_url = "https://apps.facebook.com/mousehunt/turn.php"

iframe_id = "iframe_canvas"
captcha_image_class_name = "mousehuntPage-puzzle-form-captcha-image"
captcha_input_class_name = "mousehuntPage-puzzle-form-code"
captcha_button_class_name = "mousehuntPage-puzzle-form-code-button"
new_code_class_name = "mousehuntPage-puzzle-form-newCode"
journal_entry_id = "journallatestentry"

def wait_for_next_horn():
    for i in range(15):
        time.sleep(60 + random.randint(0, 15))
        print(i+1, end=" ", flush=True)
    print()

def sound_the_horn():
    driver.get(horn_url)
    check_captcha()

def check_captcha():
    try:
        iframe = driver.find_element_by_id(iframe_id)
        driver.switch_to_frame(iframe)

        captcha = driver.find_element_by_class_name(captcha_image_class_name)
        image_url = captcha.value_of_css_property("background-image")[5:-2] # url("____")
        text = read_captcha(image_url)
        if (len(text) != 5):
            raise InvalidCaptchaException()

        driver.find_element_by_class_name(captcha_input_class_name).send_keys(text)
        driver.find_element_by_class_name(captcha_button_class_name).click()
        driver.switch_to_default_content()

        print("Captcha at:", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "-", text)
        sound_the_horn()
    except NoSuchElementException:
        print("Buwuu")
        print(get_latest_entry())
    except WebDriverException as e:
        # sometimes encounter the issue where the captcha button was an unclickable element
        driver.get(game_url)
        check_captcha()
    except InvalidCaptchaException: # enter 
        change_captcha()
        check_captcha()

def change_captcha():
    driver.get(game_url)
    iframe = driver.find_element_by_id(iframe_id)
    driver.switch_to_frame(iframe)
    
    new_captcha = driver.find_element_by_class_name(new_code_class_name)
    new_captcha.find_element_by_tag_name("a").click()

    driver.switch_to_default_content()
    driver.get(game_url)    

def get_latest_entry():
    # switch to iframe if available - not available when captcha
    try:
        iframe = driver.find_element_by_id(iframe_id)
        driver.switch_to_frame(iframe)
    except NoSuchElementException:
        pass

    # avoid halting the entire process when no journal entry is found
    try:
        text = driver.find_element_by_id(journal_entry_id).text
        driver.switch_to_default_content()
        return text
    except NoSuchElementException:
        return "Could not find journal entry"

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("log-level=2")
    driver = webdriver.Chrome(chrome_options=options)
    driver.delete_all_cookies()

    # log into facebook
    driver.get(login_url)
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("pass").send_keys(password)
    driver.find_element_by_id("loginbutton").click()
    print("Logged in")

    # await horning
    driver.get(game_url)
    print("Ready")

    while True:
        sound_the_horn()
        wait_for_next_horn()
