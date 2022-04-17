from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import glob
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.encryption import *
import os
import datetime
from modules import datetime_management
from definitions import ROOT_DIR
from config.wordpress import *

import sys
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    pass

if getattr(sys, 'frozen', False):
    path_dir = str(os.path.dirname(sys.executable))
else:
    path_dir = os.path.join(ROOT_DIR, "config")

secrets = path_dir+'/secrets.json'
with open(secrets) as f:
    secret = json.load(f)

downloads_path = os.path.join(ROOT_DIR, "downloads")

########################################################################################################################
# FUNCTIONS
########################################################################################################################
def enable_download_in_headless_chrome(driver, download_dir):
    # SOURCE: https://stackoverflow.com/questions/45631715/downloading-with-chrome-headless-and-selenium
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
    return driver

def clean_download_dir():
    # https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
    files = glob.glob(downloads_path+"/*")
    for f in files:
        os.remove(f)

# CLEAN DOWNLOADED DATAFRAME FUNCTION
def clean_df(df):
    # CONVERT TO DATE AND TIME FORMAT AND REMOVE OLD DATES
    # https://stackoverflow.com/questions/29886609/find-most-recent-date-in-pandas-dataframe
    df['Reservation_time'] = pd.to_datetime(df['Reserveringstijd'])  # convert to datetime format
    df['start time'] = df['Reservation_time'].dt.time
    df['date'] = df['Reservation_time'].dt.date
    df['numeric_date'] = df["Reservation_time"].apply(datetime_management.to_integer)
    return df


def get_latest_csv(min_treshold_time=600, max_treshold_time=0.1):
    print("CHECKING FOR CSV FILES FROM DOWNLOAD FOLDER")
    files = glob.glob(downloads_path + "/**/*", recursive = True)
    if not files:
        df = pd.DataFrame()
    else:
        latest_file = max(files, key=os.path.getctime)
        creation_time = datetime_management.modification_date(latest_file)
        current_time = datetime.datetime.now()
        # check if file is more recent than 2 minutes ago
        if (current_time.minute - min_treshold_time) < creation_time.minute < (current_time.minute + max_treshold_time) and ("csv" in str(latest_file)):
            print("LATEST CSV FILE CREATED SHORTER THAN", min_treshold_time,"MINUTES AGO, USING THIS CSV FILE")
            df = pd.read_csv(latest_file)
            df = clean_df(df)
        else:
            df = pd.DataFrame()
    return df


def get_agenda(headless=True): # change to True if way is found to download with headless browser

    clean_download_dir()

    # LOAD LOGIN INFO
    secrets = path_dir+'/secrets.json'
    with open(secrets) as f:
        secret = json.load(f)
    username = decrypt_message(secret["username_WP"].encode('utf-8'))
    password = decrypt_message(secret["password_WP"].encode('utf-8'))
    # LOG IN
    print("LOGGING IN IN WORDPRESS")
    options = Options()
    # https://stackoverflow.com/questions/63783983/element-not-interactable-in-selenium-chrome-headless-mode
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    driver = enable_download_in_headless_chrome(driver, downloads_path)
    wait = WebDriverWait(driver, 10)
    driver.get(inlog_url)
    user_input = driver.find_element_by_id('user_login')
    user_input.send_keys(username)
    element = wait.until(EC.element_to_be_clickable((By.ID, "user_pass")))
    password_input = driver.find_element_by_id('user_pass')
    password_input.send_keys(password)
    element = wait.until(EC.element_to_be_clickable((By.ID, 'wp-submit')))
    login_button = driver.find_element_by_id('wp-submit')
    login_button.click()
    # time.sleep(0.5)

    # GO TO AGENDA WEBPAGE AND PRESS DOWNLOAD CSV FILE
    print("DOWNLOADING AGENDA")
    driver.get(agenda_webpage)
    try:
        wait2 = WebDriverWait(driver, 5)
        element = wait2.until(EC.element_to_be_clickable((By.XPATH, x_path_1)))
        driver.find_element_by_xpath(x_path_1).click()
        # time.sleep(1)
    except Exception as e:
        print("COOKIES ALREADY EXCEPTED ")
    element = wait.until(EC.element_to_be_clickable((By.XPATH, x_path_2)))
    driver.find_element_by_xpath(x_path_2).click()
    element = wait.until(EC.element_to_be_clickable((By.XPATH, x_path_3)))
    download_button = driver.find_element_by_xpath(x_path_3)
    driver.implicitly_wait(10)
    ActionChains(driver).move_to_element(download_button).click(download_button).perform()
    time.sleep(5)
    driver.close()

    # FIND CSV FILE ON COMPUTER IN DOWNLOAD FOLDER
    print("READING CSV FILE FROM DOWNLOAD FOLDER")
    df = get_latest_csv()
    return df


if __name__ == '__main__':
    headless = True
    df = get_agenda(headless=headless)
    print(df)

