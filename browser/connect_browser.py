from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import path
import os
from os import path
import sys
from definitions import ROOT_DIR
from fake_useragent import UserAgent


# CHECK IF FILE IS FROZEN
here_dir = path.dirname(__file__)

def connect_browser(headless=True):
    browser_file = ROOT_DIR + "/config/browsersession.txt"
    if getattr(sys, 'frozen', False):
        os.chdir(path.dirname(sys.executable))
    with open(browser_file, "r") as f:
        executor = f.readline()
        session_id = f.readline()
    if headless == True:
        options = Options()

        # create different user agent every start browser
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f'user-agent={user_agent}')

        # create invisible browser
        options.add_argument("--headless")

        # create driver
        driver = webdriver.Remote(command_executor=executor, desired_capabilities={}, options=options)
        driver.session_id = session_id
    else:
        driver = webdriver.Chrome()
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    return driver
