from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import path
import sys
import os
from definitions import ROOT_DIR

# DEFINE PATH
if getattr(sys, 'frozen', False):
    path_dir = str(os.path.dirname(sys.executable))
else:
    path_dir = os.getcwd()

here_dir = path.dirname(__file__)

def save_browser_session(input_driver):
    driver = input_driver
    executor_url = driver.command_executor._url
    session_id = driver.session_id
    print("executor url = ", executor_url, "session id = " , session_id)
    browser_file = ROOT_DIR+"/config/browsersession.txt"
    if getattr(sys, 'frozen', False):
        os.chdir(path.dirname(sys.executable))
    with open(browser_file, "w") as f:
        f.write(executor_url)
        f.write("\n")
        f.write(session_id)
    print("BROWSERSESSION SUCCESFULLY SAVED IN", path.dirname(sys.executable))
    if getattr(sys, 'frozen', False):
        # os.chdir(sys._MEIPASS)
        pass

