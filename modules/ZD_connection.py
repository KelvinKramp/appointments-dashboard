from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from browser.connect_browser import connect_browser
from modules.encryption import *
import sys
from definitions import ROOT_DIR


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
testenv_file = os.path.join(path_dir, 'testenv.json')

# define_x_paths
website_link = "https://www.zorgdomein.nl/auth/login?redirectUrl=%2Fauth%2F"
login_page = "https://www.zorgdomein.nl/auth/login?redirectUrl=%2Fauth%2F"
username_box = "/html/body/zd-root/zd-login/zd-single-card-page/zd-application/zd-application-main/div/zd-application-main-content/div/div/zd-card/div[2]/zd-single-card-page-content/zd-card-section[2]/zd-login-form/form/zd-form-group[1]/div[2]/zd-form-input/input"
password_box = "/html/body/zd-root/zd-login/zd-single-card-page/zd-application/zd-application-main/div/zd-application-main-content/div/div/zd-card/div[2]/zd-single-card-page-content/zd-card-section[2]/zd-login-form/form/zd-form-group[2]/div[2]/zd-form-input/input"
username = decrypt_message(secret["username_ZD"].encode('utf-8'))
password = decrypt_message(secret["password_ZD"].encode('utf-8'))
inlog_button = "/html/body/zd-root/zd-login/zd-single-card-page/zd-application/zd-application-main/div/zd-application-main-content/div/div/zd-card/div[2]/zd-single-card-page-content/zd-card-section[2]/zd-login-form/form/zd-button-bar/button/zd-icon/span"
reactiva = "/html/body/zd-root/zd-select-role/zd-single-card-page/zd-application/zd-application-main/div/zd-application-main-content/div/div/zd-card/div[2]/zd-single-card-page-content/zd-card-section/form/div[1]/zd-form-group/div[2]/zd-form-radio-group/div/div/zd-form-radio-group-option/zd-form-radio/div/label"
RBH = "/html/body/zd-root/zd-select-role/zd-single-card-page/zd-application/zd-application-main/div/zd-application-main-content/div/div/zd-card/div[2]/zd-single-card-page-content/zd-card-section/form/div[2]/zd-form-group/div[2]/zd-form-radio-group/div/div/zd-form-radio-group-option/zd-form-radio/div/label"
doorgaan ="/html/body/zd-root/zd-select-role/zd-single-card-page/zd-application/zd-application-main/div/zd-application-main-content/div/div/zd-card/div[2]/zd-single-card-page-content/zd-card-section/form/zd-button-bar/button"
account_button = "/html/body/zd-root/zd-dashboard/zd-application/zd-application-header/zd-application-navigation-bar/div/zd-user-menu/div/div[2]/div[1]/zd-person-avatar/div"
logout_button = "/html/body/zd-root/zd-dashboard/zd-application/zd-application-header/zd-application-navigation-bar/div/zd-user-menu/zd-dropdown-menu/div/div/zd-dropdown-menu-item[6]/zd-icon/span"
opnieuw_inlog_button = "/html/body/zd-root/zd-logout/zd-single-card-page/zd-application/zd-application-main/div/zd-application-main-content/div/div/zd-card/div[2]/zd-single-card-page-content/zd-card-section/zd-grid-row[1]/zd-grid-cell/a/zd-icon/span"


def open_tab_and_login():
    global driver, wait
    driver = connect_browser()
    wait = WebDriverWait(driver, 10)
    print("CONNECTION TO BROWSER SUCCESFULL")
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    counter = 0
    while True:
        login()
        if check_sms_verificatie():
            return
        elif check_select_page():
            return
        elif counter == 5:
            break
        else:
            time.sleep(sleep_par_long)
            pass

def login():
    print("RUNNING LOGIN FUNCTION")
    secrets = path_dir+'/secrets.json'
    with open(secrets) as f:
        secret = json.load(f)
    username = decrypt_message(secret["username_ZD"].encode('utf-8'))
    password = decrypt_message(secret["password_ZD"].encode('utf-8'))
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

def check_select_page():
    driver = connect_browser()
    text = driver.page_source
    if "Selecteer organisatie, functie en locatie" in text:
        print("REACHED ORGANISATAION SELECTION PAGE")
        return True
    else:
        try:
            login()
        except Exception as e:
            # TRY TO LOGOUT AND IN BY CLICKING ON BUTTONS OF ZORGDOMEIN
            try:
                logout_and_in()
                text = driver.page_source
                if "Selecteer organisatie, functie en locatie" in text:
                    print("REACHED ORGANISATAION SELECTION PAGE")
                    return True
            except Exception as e:
                print("GRACEFULL LOGOUT NOT SUCCEEDED")
                print("THE FOLLOWING ERROR OCCURED")
                print(e)
                return False


def select_orga(orga):
    with open(testenv_file) as f:
        testenv = json.load(f)
    dev_switch = eval(testenv["state"])
    if not dev_switch:
        b = check_select_page()
        if not b:
            print("TEST1")
            return b
        else:
            if orga == "RBH":
                orga_x_path = RBH
            elif orga == "REA":
                orga_x_path = reactiva
            element = wait.until(EC.element_to_be_clickable((By.XPATH, orga_x_path)))
            driver.find_element_by_xpath(orga_x_path).click()
            element = wait.until(EC.element_to_be_clickable((By.XPATH, doorgaan)))
            driver.find_element_by_xpath(doorgaan).click()
            time.sleep(sleep_par_short)
            return b
    else:
        return True


def logout_and_in():
    element = wait.until(EC.element_to_be_clickable((By.XPATH, account_button)))
    driver.find_element_by_xpath(account_button).click()
    element = wait.until(EC.element_to_be_clickable((By.XPATH, logout_button)))
    driver.find_element_by_xpath(logout_button).click()
    element = wait.until(EC.element_to_be_clickable((By.XPATH, opnieuw_inlog_button)))
    driver.find_element_by_xpath(opnieuw_inlog_button).click()
    time.sleep(sleep_par_short)