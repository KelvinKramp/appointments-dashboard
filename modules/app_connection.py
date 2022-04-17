from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from browser.connect_browser import connect_browser
from modules.encryption import *
import sys
from definitions import ROOT_DIR
import os
import json

if getattr(sys, 'frozen', False):
    path_dir = str(os.path.dirname(sys.executable))
else:
    path_dir = os.path.join(ROOT_DIR, "config")

secrets = path_dir+'/secrets.json'
with open(secrets) as f:
    secret = json.load(f)

# define sleep parameter
sleep_par_short = 0.1
sleep_par_long = 0.5

# define_x_paths
website_link = "..."
login_page = "..."
select_orga_page = "..."
username_box = "..."
password_box = "..."
username = "..."
password = "..."
inlog_button = "..."
reactiva = "..."
RBH = "..."
doorgaan = "..."
account_button = "..."
logout_button = "..."
opnieuw_inlog_button = "..."

# testenv file
testenv_file = os.path.join(path_dir, 'testenv.json')


def open_tab():
    global driver, wait
    driver = connect_browser()
    wait = WebDriverWait(driver, 10)
    print("CONNECTION TO BROWSER SUCCESFULL")
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    print("EXTRA TAB OPENED")


def login():
    print("RUNNING LOGIN FUNCTION")
    secrets = path_dir+'/secrets.json'
    with open(secrets) as f:
        secret = json.load(f)
    username = decrypt_message(secret["username_1"].encode('utf-8'))
    password = decrypt_message(secret["password_1"].encode('utf-8'))
    time.sleep(sleep_par_short)
    driver.get(login_page)
    element = wait.until(EC.element_to_be_clickable((By.ID, "username")))
    driver.find_element_by_id("username").clear()
    element = wait.until(EC.element_to_be_clickable((By.ID, "username")))
    driver.find_element_by_id("username").send_keys(username)
    element = wait.until(EC.element_to_be_clickable((By.ID, "password")))
    driver.find_element_by_id("password").clear()
    element = wait.until(EC.element_to_be_clickable((By.ID, "password")))
    driver.find_element_by_id("password").send_keys(password)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, inlog_button)))
    driver.find_element_by_xpath(inlog_button).click()
    time.sleep(sleep_par_long)


def check_sms_verificatie():
    text = driver.page_source
    if "verificatie" in text:
        print("REACHED SMS VERIFICATION")
        return True
    else:
        return False


def try_n_loggins():
    counter = 0
    max_tries = 3
    while True:
        time.sleep(sleep_par_long)
        if check_select_page():
            return True
        elif check_sms_verificatie():
            return False
        elif counter == max_tries:
            print("COULD NOT LOGIN AFTER", max_tries, "TRIES")
            return False
        else:
            login()
            time.sleep(sleep_par_long)
            counter += 1


def check_select_page():
    driver = connect_browser()
    # Wait for the new window or tab
    wait = WebDriverWait(driver, 10)
    wait.until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[1])
    driver.get(select_orga_page)
    time.sleep(sleep_par_long)
    text = driver.page_source
    if "Doorgaan" in text:
        print("REACHED ORGANISATAION SELECTION PAGE")
        return True
    else:
        return False


def select_orga(orga):
    with open(testenv_file) as f:
        testenv = json.load(f)
    dev_switch = eval(testenv["state"])
    if not dev_switch:
        b = check_select_page()
        if not b:
            try_n_loggins()
        if orga == "RBH":
            orga_x_path = RBH
        elif orga == "REA":
            orga_x_path = reactiva
        element = wait.until(EC.element_to_be_clickable((By.XPATH, orga_x_path)))
        driver.find_element_by_xpath(orga_x_path).click()
        element = wait.until(EC.element_to_be_clickable((By.XPATH, doorgaan)))
        driver.find_element_by_xpath(doorgaan).click()
        time.sleep(sleep_par_short)
        return True
    else:
        return True


# currently not used
def logout_and_in():
    element = wait.until(EC.element_to_be_clickable((By.XPATH, account_button)))
    driver.find_element_by_xpath(account_button).click()
    element = wait.until(EC.element_to_be_clickable((By.XPATH, logout_button)))
    driver.find_element_by_xpath(logout_button).click()
    element = wait.until(EC.element_to_be_clickable((By.XPATH, opnieuw_inlog_button)))
    driver.find_element_by_xpath(opnieuw_inlog_button).click()
    time.sleep(sleep_par_short)
