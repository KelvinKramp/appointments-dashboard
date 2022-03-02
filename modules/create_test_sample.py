import pandas as pd
import names
import random
from modules import datetime_management
import os

test_csv = "test_csv_file.csv"

# DEFINE FUNCTIONS
def to_integer(dt_time):
    return 10000000000*dt_time.year + 100000000*dt_time.month + 1000000*dt_time.day + 10000*dt_time.hour + 100*dt_time.minute + dt_time.second


def create_test_sample(n=16):
    # IF LAST APPOINTMENT TIME IN LAST CREATED TEST SAMPLE IS EARLIER THAN CURRENT TIME, LOAD LAST TEST SAMPLE
    t = datetime_management.currentTimeUTC()
    if os.path.exists(test_csv) and pd.read_csv(test_csv)["Reserveringstijd"].iloc[-1] < t:
        return pd.read_csv("test_csv_file.csv")

    # CREATE RANDOM NAMES
    def random_names(n):
        name_list = []
        for i in range(n):
            name = names.get_full_name()
            name_list.append(name)
        return name_list

    # CREATE RANDOM PHONE NUMBER
    def random_phone_number(n):
        phone_numbers_list = []
        for i in range(n):
            random_time = str(random.random())  # creates random number between 0 and 1
            random_8_digits = random_time[-8:]
            phone_number = "06" + random_8_digits
            phone_numbers_list.append(str(phone_number))
        return phone_numbers_list

    # RANDOMLY CHOSE ORGANISATION FOR CLIENT
    def random_choice_orga(n):
        orga_list = []
        orga_options = ["75+ Keuring rijbewijs A/B/BE", "Medische keuring rijbewijs A/B/BE",
                        "Rijbewijskeuring groot (C/D/E)"]
        for i in range(n):
            orga = random.choice(orga_options)
            orga_list.append(orga)
        return orga_list


    # CREATE OTHER LISTS
    def other_lists(n):
        duur_list = n * ["15 min"]
        status_list = n * ["Goedgekeurd"]
        betaling_list = n * ["€0,00 van €69,95 Lokaal In afwachting"]
        return duur_list, status_list, betaling_list


    # CREATE APPOINTMENT TIMES
    def appointment_times(n):
        from datetime import datetime as dt
        from datetime import timedelta
        current_time = dt.now()
        time_list = []
        for i in range(n):
            add_time = current_time + timedelta(seconds=5)
            time_list.append(add_time.strftime("%Y-%m-%d %H:%M:%S"))
            current_time = add_time
        return time_list

    # CREATE RANDOM EMAIL
    def e_mail_generator(list_of_names):
        e_mail_list = []
        for i in list_of_names:
            name = i
            e_mail_list.append(name.split(" ")[0] + "@mail.com")
        return e_mail_list

    duur_list, status_list, betaling_list = other_lists(n)
    orga_list = random_choice_orga(n)
    phone_numbers_list = random_phone_number(n)
    name_list = random_names(n)
    time_list = appointment_times(n)
    e_mail_list = e_mail_generator(name_list)
    empty_list = n * ["NaN"]

    # CREATE AND CLEAN DF
    for i in [duur_list, orga_list, phone_numbers_list, name_list, time_list, e_mail_list, empty_list]:
        if len(i) == 16:
            pass
        else:
            raise Exception("length lists not equal")
    d = {'Reserveringstijd': time_list, 'Klantnaam': name_list, 'Klant Telefoon': phone_numbers_list,
         'Klant E-mail': e_mail_list, 'Dienst': orga_list, 'Duur': duur_list, 'Status': status_list,
         'Betaling': betaling_list, 'Opmerkingen. Let op: deel hier géén medische informatie. ': empty_list}
    df = pd.DataFrame(data=d)
    df['Reservation_time'] = pd.to_datetime(df['Reserveringstijd'])  # convert to datetime format
    df['start time'] = df['Reservation_time'].dt.time
    df['date'] = df['Reservation_time'].dt.date
    df['numeric_date'] = df["Reservation_time"].apply(to_integer)

    # SAVE DF AS CSV FILE
    df.to_csv("test_csv_file.csv")
    print("new csv file created")
    return df


if __name__ == '__main__':
    df = create_test_sample()