import os
import random
import time

from tweepy.streaming import json

from keys import *
from selenium import webdriver
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

from strings import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

current_total = 0

MY_SCREEN_NAME = '2048Robot'
# don't be an idiot by hardcoding your password in the actual script
MY_PASSWORD = open("mypassword.txt").read().strip()

browser = None
wait = WebDriverWait(browser, 120)


def click(selector, repeat=1):
    wait = WebDriverWait(browser, 120)
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    for i in range(0, repeat):
        element.click()

def click_xpath(xpath, repeat=1):
    wait = WebDriverWait(browser, 120)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    for i in range(0, repeat):
        element.click()

def post_image(last_poll, round):
    global current_total
    if current_total == 23 :
        temp_last = last_poll
        last_poll = send_tweet("We continue here the game from this thread: ", last_poll)
        current_total = 0
        reply("The game continues in the following thread: " + last_poll, temp_last)
    api.update_with_media("/home/david/2048Bot/" + str(round) + ".png", status="Round " + str(round) + "!!", in_reply_to_status_id=last_poll.split('/')[-1])
    current_total += 1
    #save new href
    return get_last_tweet_href()

def post_poll(last_poll, round):
    wait = WebDriverWait(browser, 120)
    browser.get(last_poll)
    global current_total
    time.sleep(3)
    click("div.stream-item-footer:nth-child(5) > div:nth-child(2) > div:nth-child(1) > button:nth-child(1)")

    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#tweet-box-global")))
    element.send_keys("Poll for round " + str(round) + "!")


    element = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[23]/div/div[2]/div[4]/form/div[3]/div[1]/span[3]/div/button")))
    element.click()
    click_xpath('/html/body/div[23]/div/div[2]/div[4]/form/div[2]/div[3]/div[3]/div/button[1]', repeat=2)

    emojies = ["", "⬆️", "⬇️", "➡️", "⬅️"]
    choices = ["", "UP ", "DOWN ", "RIGHT ", "LEFT️ "]

    time.sleep(3)

    for j in range(1, 5):
        browser.find_element_by_xpath('/html/body/div[23]/div/div[2]/div[4]/form/div[2]/div[3]/div[3]/div/div[' + str(j) + ']/div[1]').send_keys(emojies[j]+emojies[j])

    click('.is-reply > div:nth-child(2) > div:nth-child(6) > div:nth-child(3) > div:nth-child(1) > div:nth-child(6) > button:nth-child(2)')

    select = Select(browser.find_element_by_xpath(
        '/html/body/div[23]/div/div[2]/div[4]/form/div[2]/div[3]/div[3]/div/div[5]/div/select'))
    select.select_by_visible_text('0')
    select = Select(browser.find_element_by_xpath(
        '/html/body/div[23]/div/div[2]/div[4]/form/div[2]/div[3]/div[3]/div/div[5]/div/spann/select'))
    select.select_by_visible_text('0')
    select = Select(browser.find_element_by_xpath(
        '/html/body/div[23]/div/div[2]/div[4]/form/div[2]/div[3]/div[3]/div/div[5]/div/spann/spann/select'))
    select.select_by_visible_text('5')
    element.send_keys(Keys.CONTROL, Keys.ENTER)
    time.sleep(5)
    current_total += 1
    return get_last_tweet_href()

def send_tweet(text, last_poll):
    api.update_status(status=text + last_poll)
    global current_total
    current_total += 1
    return get_last_tweet_href()

def reply(text, last_poll):
    api.update_status(status=text, in_reply_to_status_id=last_poll.split('/')[-1])
    global current_total
    current_total += 1
    return get_last_tweet_href()

def check_poll_results(href):
    browser.get('https://twitter.com/2048Robot')
    time.sleep(3)
    elem = browser.find_element_by_css_selector("div.js-macaw-cards-iframe-container:nth-child(1)")
    print(elem.get_attribute('data-src'))
    browser.get('http://twitter.com' + str(elem.get_attribute('data-src')))
    time.sleep(3)
    results = []
    pos = ["UP", "DOWN", "RIGHT", "LEFT"]
    for i in range(1,5):
        elem = browser.find_element_by_css_selector("div.TwitterCardsGrid-col--12:nth-child(" + str(i) + ") > label:nth-child(1) > span:nth-child(4)")
        results.append(int((elem.text).split('%')[0]))
    if max(results) == 0:
        return pos[random.randint(0, 3)]
    else:
        return pos[results.index(max(results))]


def login():
    global browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Runs Chrome in headless mode.
    options.add_argument('--no-sandbox')  # # Bypass OS security model
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    # Operating in headless mode
    browser = Chrome(executable_path=os.path.abspath("/home/david/2048Bot/chromedriver"), chrome_options=options)
    browser.get('https://twitter.com/login/error')
    el = browser.find_element_by_xpath(username)
    el.send_keys(MY_SCREEN_NAME)
    el = browser.find_element_by_xpath(password)
    el.send_keys(MY_PASSWORD)
    # Submit the form
    el.send_keys(Keys.TAB)
    el.send_keys(Keys.ENTER)
    return browser


def get_last_tweet_href():
    # Opens the profile url and retrieves de last tweet's url
    tweet = api.user_timeline(id=api.me().id, count=1)[0]
    return 'https://twitter.com/2048Robot/status/' + str(tweet.id)
