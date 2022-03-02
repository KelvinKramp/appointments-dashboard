import time
import threading as thr
from selenium import webdriver
from browser.save_browser_session import save_browser_session
import subprocess
import os
import sys
from os import path
import json
from browser.connect_browser import connect_browser
from definitions import ROOT_DIR

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    pass


def create_empty_secrets_json_file(secrets_file):
    data = {
            "username_1": "gAAAAABhGgq6EOcbszKzW7KuYq8-Ns8mZGEnqj051zWeR4-wUT5Clq51JD-2sZ-EDDKEVdZ3QuHCjtjVKGkmBA3CPcfpG0Mszg==",
            "password_1": "gAAAAABhGgq6EOcbszKzW7KuYq8-Ns8mZGEnqj051zWeR4-wUT5Clq51JD-2sZ-EDDKEVdZ3QuHCjtjVKGkmBA3CPcfpG0Mszg==",
            "username_WP": "gAAAAABhGgq6EOcbszKzW7KuYq8-Ns8mZGEnqj051zWeR4-wUT5Clq51JD-2sZ-EDDKEVdZ3QuHCjtjVKGkmBA3CPcfpG0Mszg==",
            "password_WP": "gAAAAABhGgq6EOcbszKzW7KuYq8-Ns8mZGEnqj051zWeR4-wUT5Clq51JD-2sZ-EDDKEVdZ3QuHCjtjVKGkmBA3CPcfpG0Mszg==",
            "email_email_comments": "gAAAAABhF2qcSpZApFq8hcTtW7BBoMmSMAMxBWI2kWq09Px-QBhSl8BfTy4A5ruiRo2NCVO7BYkDQZ6MxKuK586Vd9GtJT2cxIl2P8rTGiVRXi-eVd3z51A=",
            "password_email_comments": "gAAAAABhFX1lyDiw6esHHxVVBpUGkrarxHjKrowAGDVaMJDfPGUVyb7pHDLOpjURM5_MfWABFE2Xfawd5SdTj4Vc0as2Wjd3pw==",
            "email_receive_comments": "gAAAAABhGgq6EOcbszKzW7KuYq8-Ns8mZGEnqj051zWeR4-wUT5Clq51JD-2sZ-EDDKEVdZ3QuHCjtjVKGkmBA3CPcfpG0Mszg=="}
    with open(secrets_file, 'w') as f:
        json.dump(data, f)


def kill_server():
    subprocess.run("lsof -t -i tcp:8080 | xargs kill -9", shell=True) # kill the server


def quit_dash_app():
    driver = connect_browser()
    driver.quit()
    subprocess.run("lsof -t -i tcp:8080 | xargs kill -9", shell=True) # kill the server
    print("EXITED")
    # python app.run_server will still be running on background...


def start_dash_app():
    subprocess.Popen("python dash_app.py", shell=True)


def start_dash_app_frozen():
    path_dir = str(path.dirname(sys.executable))
    subprocess.Popen(path_dir+"/dash_app", shell=False)


def start_driver():
    driver1 = webdriver.Chrome()
    counter = 0
    while True:
        try:
            counter += 1
            driver1.get("http://0.0.0.0:8080/")  # Dash app runs on a LOCAL server!
            break
        except Exception as e:
            if counter == 5:
                print("TRIED TO REACH LOCALSERVER 5 TIMES, EXITING PROGRAM")
                quit_dash_app()
            else:
                print("COULD NOT REACH LOCAL SERVER, TRYING AGAIN")
        time.sleep(3)
    save_browser_session(driver1)
    print("DRIVER SAVED IN TEXT FILE browsersession.txt")


def keep_server_running():
    while True:
        time.sleep(60)
        print("Next run for 60 seconds")


def main():
    kill_server()
    try:
        executable_dir = str(sys._MEIPASS)
    except Exception as e:
        print("RUNNING NON-EXECUTABLE")
        executable_dir = "NON EXISTENT DIRECTORY"
    if getattr(sys, 'frozen', False):
        path_dir = str(path.dirname(sys.executable))
    else:
        path_dir = os.path.join(ROOT_DIR, "config")
    secrets_file = path_dir + "/secrets.json"
    if os.path.isfile(secrets_file):
        pass
    else:
        create_empty_secrets_json_file(secrets_file)
    if executable_dir in os.getcwd():
        print("FILENAME = ", __file__)
        print("STARTING FROZEN DASH APP")
        thread = thr.Thread(target=start_dash_app_frozen)
        thread.start()
    else:
        print("FILENAME = ", __file__)
        print("STARTING UNFROZEN DASH APP")
        thread = thr.Thread(target=start_dash_app)
        thread.start()
    start_driver()
    keep_server_running()


if __name__ == '__main__':
    main()