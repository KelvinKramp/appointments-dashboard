from modules.app_connection import *
from modules.encryption import *

# PARSE TABLE INFO AND GET COLOR AND ORGANISATION
def define_color(df_4_color, row_number_client): # could raise issues in case that row_number_client = -1
    color,orga = 'white', "RBH" # initialize variables
    for i, j in enumerate(df_4_color["Dienst"]):
        if i == row_number_client:
            matches = ["75", "Medische"]
            if any(x in j for x in matches):
                color = 'darkred'
                orga = "RBH"
            else:
                color = 'darkblue'
                orga = "REA"
    return color, orga
