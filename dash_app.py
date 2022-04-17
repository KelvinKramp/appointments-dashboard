########################################################################################################################
########################################################################################################################
# IMPORT MODULES
import dash
from dash import html
from dash.dependencies import Input, Output, State
from dash import dcc
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd
from datetime import datetime as dt
from datetime import date
from modules.create_test_sample import create_test_sample
from modules import create_empty_secrets_file
from modules import download_wp_agenda
from modules.perf_var_calc import perf_var_calc
from modules.app_connection import *
from selenium import webdriver
from browser.save_browser_session import save_browser_session
from threading import Timer
import dash_daq as daq
import subprocess
from modules.email_comments import send_email, toaddr, send_email_developer
from modules.encryption import *
import os.path
from browser.connect_browser import connect_browser
from modules import datetime_management
from modules import client_selection
from definitions import ROOT_DIR, empty_byte_string
import modules.app_connection as app_connection
from dateutil import parser

########################################################################################################################
########################################################################################################################
# NOTES
# table styling
# https://community.plotly.com/t/updating-a-variable-used-in-datatables-style-data-conditional/32827/7
# logging
# https://stackoverflow.com/questions/50144628/python-logging-into-file-as-a-dictionary-or-json
# css colors
# https://developer.mozilla.org/en-US/docs/Web/CSS/color_value#color_keywords
# automatically open browser in dash
# https://community.plotly.com/t/auto-open-browser-window-with-dash/31948
# opening and closing tabs in selenium
# https://www.geeksforgeeks.org/opening-and-closing-tabs-using-selenium/
# getting exe file to work with pyinstaller by right referencing
# https://stackoverflow.com/questions/59238237/why-use-getattr-instead-of-hasattr-for-sys-frozen


########################################################################################################################
########################################################################################################################
# CHANGE CURRENT WORKING DIRECTORY AND FILEPATH

# CHANGE DIR IF FILE IS FROZEN
import sys
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    pass

# SET FILE PATH ACCORDING TO FROZEN OR NON FROZEN SATE
if getattr(sys, 'frozen', False):
    path_dir = str(os.path.dirname(sys.executable))
else:
    path_dir = os.path.join(ROOT_DIR, "config")


########################################################################################################################
########################################################################################################################
# FILE ADMINISTRATION
# CREATE CLEAN LOGGING FILE
loggingsfile = path_dir+'/loggings.json'
with open(loggingsfile, 'w') as f:
    clean_list = []
    json.dump(clean_list, f)

# OPEN ENCRYPTED SECRETS FILE
secrets = path_dir+'/secrets.json'
with open(secrets) as f:
    secret = json.load(f)


########################################################################################################################
########################################################################################################################
# FUNCTIONS


def quit_dash_app():
    driver = connect_browser()
    driver.quit()
    subprocess.run("lsof -t -i tcp:8080 | xargs kill -9", shell=True) # kill the server
    print("EXITED")
    # python app.run_server will still be running on background...


# OPEN BROWSER WITH DASH APP AT STARTUP OF APP
def open_browser():
    # driver for Dash app is called driver1 to avoid confusion with the
    # other driver used to control second tab
    driver1 = webdriver.Chrome()
    driver1.get("http://0.0.0.0:8080/") # Dash app runs on a LOCAL server!
    save_browser_session(driver1)


# CREATE LOGGING JSON FILE
def addLogging(logDict:dict):
    loggingsFile = path_dir+'/loggings.json'
    with open(loggingsFile) as f:
        data = json.load(f)
    data.append(logDict)
    with open(loggingsFile, 'w') as f:
        json.dump(data, f)


def empty_dataframe():
    df = pd.DataFrame(index=[0],
                      columns=["Reserveringstijd", "Klantnaam", "Klant Telefoon", "Klant E-mail", "Dienst",
                               "Duur", "Status", "Betaling",
                               "Opmerkingen. Let op: deel hier géén medische informatie.", 'Reservation_time',
                               'start time', 'date', 'numeric_date'])
    return df


def get_data(date_picker_output):
    # IF NO DATE SELECTED RETURN EMPTY DF
    if not date_picker_output:
        return empty_dataframe()

    # CHECK WHETHER IN TEST ENV
    with open(testenv_file) as f:
        testenv = json.load(f)
    dev_switch = eval(testenv["state"])

    # IF IN TEST ENV CREATE SAMPLE DF
    if dev_switch:
        df = create_test_sample()
        return df
    # IF NOT IN TEST ENV GET DATAFRAME
    else:
        df = download_wp_agenda.get_latest_csv()  # return df from csv in downloads folder
        if df.empty: # if no csv is found download agenda from wordpress
            df = download_wp_agenda.get_agenda()
        df = download_wp_agenda.clean_df(df)
        date_picker_output = parser.parse(date_picker_output)
        df = datetime_management.filter_df_on_date(df, date_picker_output)
        return df


def read_data():
    df = pd.read_csv("test_csv_file.csv")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df


########################################################################################################################
########################################################################################################################
# DEFINE VARIABLES

# READ WHETHER IN TEST-ENVIRONMENT
testenv_file = os.path.join(path_dir,'testenv.json')
with open(testenv_file) as f:
    testenv = json.load(f)
dev_switch = eval(testenv["state"])

# IF SECRETS FILE IS EMPTY START WITH MODAL WINDOW FOR ENTERING USER INFO
if (str(decrypt_message(secret["username_WP"].encode('utf-8'))) == "") and not dev_switch:
    bool_user_info = True
else:
    bool_user_info = False

download_excell_filename = "output.xlsx"
df = empty_dataframe()

########################################################################################################################
########################################################################################################################
# THE APP LAYOUT
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.title = 'Appointments dashboard'
server = app.server
app.layout = html.Div(
    style={'textAlign': 'center', 'margin': 'auto'},
    children=[
        dbc.Row(children=[
            html.Br(),
        ]),
        dbc.Row([
            dbc.Col(html.H1("AGENDA", style={'textAlign': 'center'}),
                    width=12)
        ]),
        dbc.Row(children=[
            dbc.Button("Start consulting", id='login', n_clicks=0, style={'display': 'True'}),
            dbc.Button("Previous client", id='previous', n_clicks=0, style={'display': 'True'}),
            dbc.Button("Next client", id='next', n_clicks=0, style={'display': 'True'}),
            dbc.Button("Info", id='test-info', n_clicks=0, style={'display': 'True'}),
            dbc.Button("Load test", id='test',  n_clicks=0, style={'display': 'True'}),
            dbc.Button("Toggle alert", id='toggle-alert', n_clicks=0),
            dcc.DatePickerSingle(
                id='input-day',
                min_date_allowed=date(2016, 8, 5),
                max_date_allowed=date(2030, 9, 19),
                initial_visible_month=dt.now(),
                display_format='D-M-Y',
                date=dt.now(),
            ),
            # dbc.Button("Quit", id='quit'),
        ],
            no_gutters=False,
            style={
                "display": "inline-block",
                "width": "80%",
                "verticalAlign": "top",
            }
        ),
        dbc.Row(children=[
            daq.BooleanSwitch(
                id='test-env-switch',
                on=dev_switch
            ),
            html.Div(" "),
            html.Div(id='boolean-switch-output'),
        ],
            style={
                "display": "inline-block",
                "width": "100%",
                "verticalAlign": "top"
            }
        ),
        dbc.Row(children=[
            dbc.Alert(
                "Example alert: Click on the datepciker and choose a date to select a list of clients",
                id="alert-fade-1",
                dismissable=True,
                is_open=False, ),
        ],
            style={
                "display": "inline-block",
                "width": "60%",
                "verticalAlign": "top"
            }),
        dbc.Row(children=[
            dash_table.DataTable(
                id='table-client-info',
                columns=[
                    {'name': 'Date', 'id': 'date', 'type': 'datetime'},
                    {'name': 'Appointment time', 'id': 'start time', 'type': 'datetime'},
                    {'name': 'Service', 'id': 'Dienst', 'type': 'text'},
                    {'name': 'Client', 'id': 'Klantnaam', 'type': 'text'},
                    {'name': 'Phone number', 'id': 'Klant Telefoon', 'type': 'text'},
                    {'name': 'Comments', 'id': 'comments', 'type': 'text', 'editable': True},
                ],
                data=df.to_dict('records'),
                style_cell={'font-family':'Source Sans Pro'},
                style_data_conditional=[],
            ),],
            style={
                "display": "inline-block",
                "width": "80%",
                "verticalAlign": "top"
            }),
        dbc.Row(children=[
            html.Br(),
        ]),
        html.Div(" "),
        dbc.Button("E-mail comments", id='send', n_clicks=0),
        dbc.Button("Notes", id='notes', n_clicks=0),
        dbc.Button("OPS score calculator", id='OPS', n_clicks=0),
        dbc.Button("User info", id='user-info', n_clicks=0),
        dbc.Button("Report a bug", id='report-bug', n_clicks=0),
        html.Div(" "),
        html.A("OPS document", href="https://www.cbr.nl/web/file?uuid=a9ed4c42-7d84-41d8-9e99-240a705ffb62&owner=d214f7b5-5ce0-48dc-a521-4ef537c9d232&contentid=702", target="_blank"),
        html.Div(" "),
        html.Div(id="perf_var"),
        html.Div(" "),
        html.Div(" "),
        html.Div(id='output-container-date-picker-single', style={'display': 'none'}),
        html.Div(id='output-quit-button', style={'display': 'none'}),
        dbc.Modal(
            [
                dbc.ModalBody(children=[html.H2("Information"),
                                        html.Div(
                                            "Sample text"),
                                        ]),

                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto", n_clicks =0)
                ),
            ],
            is_open=False,
            id="modal",
            style = {"white-space":"break-spaces"},
            backdrop=False
        ),

        # LOGIN MODAL WINDOW
        dbc.Modal(
            [
                dbc.ModalHeader("Login"),
                dbc.ModalBody("Login in the second tab to start consultations and click on ready"),
                dbc.ModalFooter(
                    dbc.Button("Ready", id="close2", className="ml-auto", n_clicks=0)
                ),
            ],
            is_open=False,
            id="modal2",
            backdrop=False

        ),

        # SEND EMAIL WITH ATTACHMENT MODAL WINDOW
        dbc.Modal(
            [
                dbc.ModalHeader(""),
                dbc.ModalBody("E-mail with comments has been send to "+ toaddr),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close3", className="ml-auto", n_clicks=0)
                ),
            ],
            is_open=False,
            id="modal3",
            style={"white-space": "break-spaces"},
            backdrop=False
        ),

        # NOTES MODAL WINDOW
        dbc.Modal(
            [
                dbc.ModalHeader("Notes"),
                dbc.ModalBody(children=(dcc.Textarea(
                    id='textarea',
                    value='',
                    style={'width': '100%', 'height': 300},
                ),)
                ),
                dbc.ModalFooter(children=[
                    dbc.Button("Save", id="close4", className="ml-auto", n_clicks=0),
                ]
                ),
            ],
            is_open=False,
            id="modal4",
            style={"white-space": "break-spaces"},
            backdrop=False
        ),

        # SCORE CALCULATOR MODAL WINDOW
        dbc.Modal(
            [
                dbc.ModalBody(children=(
                    html.Div(children=[
                        html.Iframe(src="https://ops-calculator.herokuapp.com/", width='100%', height='100%'),],
                            style={'textAlign': 'center', 'margin': 'auto','width': '100%',"height": "70vh"},),),),
                dbc.ModalFooter(children=[
                    dbc.Button("Close", id="close5", className="ml-auto", n_clicks=0),
                ]
                ),
            ],
            is_open=False,
            id="modal5",
            style={"white-space": "break-spaces","max-width": "none", "width": "100%", "height":"100%"},
            backdrop=False
        ),

        # USER INFORMATION MODAL WINDOW
        dbc.Modal(
            [
                dbc.ModalBody(children=(
                    html.Div(children=[
                        html.H5("Username 1"),
                        dcc.Input(
                                    id="username_1",
                                    type='email',
                                    value=str(decrypt_message(secret["username_1"].encode('utf-8'))),
                                ),
                        html.Div(""),
                        html.H5("Password 1"),
                        dcc.Input(
                            id="password_1",
                            type='password',
                            value=str(decrypt_message(secret["password_1"].encode('utf-8'))),
                        ),
                        html.Div(""),
                        html.H5("Wordpress username"),
                        dcc.Input(
                            id="username_WP",
                            type='text',
                            value=str(decrypt_message(secret["username_WP"].encode('utf-8'))),
                        ),
                        html.Div(""),
                        html.H5("Wordpress password"),
                        dcc.Input(
                            id="password_WP",
                            type='password',
                            value=str(decrypt_message(secret["password_WP"].encode('utf-8'))),
                        ),
                        html.Div(""),
                        html.H5("E-mail address to send comments to"),
                        dcc.Input(
                            id="email_receive_comments",
                            type='email',
                            value=str(decrypt_message(secret["email_receive_comments"].encode('utf-8'))),
                        )
                    ],style={'textAlign': 'center'},
                    ),), ),
                dbc.ModalFooter(children=[
                    dbc.Button("Save", id="close6", className="ml-auto", n_clicks=0),
                ]
                ),
            ],
            is_open=bool_user_info,
            id="modal6",
            style={"white-space": "break-spaces", "max-width": "none", "width": "50%", "height": "100%"},
            backdrop=False
        ),

        # REPORT BUG MODAL WINDOW
        dbc.Modal(
            [
                dbc.ModalHeader("Report a bug"),
                dbc.ModalBody(children=(dcc.Textarea(
                    id='textarea7',
                    value='',
                    style={'width': '100%', 'height': 300},
                ),)
                ),
                dbc.ModalFooter(children=[
                    dbc.Button("Send", id="send7",  n_clicks=0,style={"horizontalAlign": "right"}),
                    dbc.Button("Close", id="close7", n_clicks=0, style={"horizontalAlign": "left"}),
                ]
                ),
            ],
            is_open=False,
            id="modal7",
            style={"white-space": "break-spaces"},
            backdrop=False
        ),

        # REFRESH THE TABLE EVERY X SECONDS
        dcc.Interval(
                id='interval-component',
                interval=1 * 500,  # refresh rate of the table in milliseconds
                n_intervals=0
            ),

        # PAGE LOADING ANIMATIONS
        dcc.Loading(
            id="loading-1",
            type="default",
            fullscreen=True,
            style={'backgroundColor': 'transparent',
                   'text-align': 'center',
                   'margin': 'auto',
                   'justify-content': 'center'
                   },
            color='darkred',
            children=[
                html.Div(id='dd-output-container-1'),
            ]
        ),
        dcc.Loading(
            id="loading-2",
            type="default",
            fullscreen=True,
            style={'backgroundColor': 'transparent',
                   'text-align': 'center',
                   'margin': 'auto',
                   'justify-content': 'center'
                   },
            color='darkred',
            children=[
                html.Div(id='dd-output-container-2'),
            ]
        ),
    ],
)



########################################################################################################################
########################################################################################################################
# DASH CALLBACKS


# ALERT (modify text in dbc.alert if needed)
@app.callback(
    Output("alert-fade-1", "is_open"),
    [Input("toggle-alert", "n_clicks")],
    [State("alert-fade-1", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('output-container-date-picker-single', 'children'),
    [Input('input-day', 'date')])
def update_output(date_value):
    if date_value is not None:
        return date_value


# QUIT BUTTON
# @app.callback(
#     Output('output-quit-button', 'children'),
#     [Input('quit', 'n_clicks')])
# def quit(quit_button_click):
#     if quit_button_click:
#         quit_dash_app()


# TEST INFO MODAL WINDOW
@app.callback(
    Output("modal", "is_open"),
    [Input("test-info", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def test_info_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# NOTES MODAL WINDOW
@app.callback(
    Output("modal4", "is_open"),
    [Input("notes", "n_clicks"), Input("close4", "n_clicks")],
    [State("modal4", "is_open")],
)
def notes_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# SCORE CALCULATOR MODAL WINDOW
@app.callback(
    Output("modal5", "is_open"),
    [Input("OPS", "n_clicks"), Input("close5", "n_clicks")],
    [State("modal5", "is_open")],
)
def OPS_score(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# USER INFORMATION
@app.callback(
    Output("modal6", "is_open"),
    [Input("user-info", "n_clicks"), Input("close6", "n_clicks"),
     Input('username_1', 'value'),
     Input('password_1', 'value'),
     Input('username_WP', 'value'),
     Input('password_WP', 'value'),
     Input('email_receive_comments', 'value'),
     ],
    [State("modal6", "is_open")],
)
def user_info(user_info, close6, username_1, password_1, username_2, password_2, email_receive_comments, is_open):
    ctx = dash.callback_context
    interaction_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if interaction_id == "user-info":
        return True
    elif interaction_id == "close6":
        # SAVE DATA
        secrets_file = ROOT_DIR +'/config/secrets.json'
        data = {"username_1": str(encrypt_message(username_1).decode("utf-8")), "password_1": str(encrypt_message(password_1).decode("utf-8") ),
                "username_WP": str(encrypt_message(username_2).decode("utf-8")), "password_WP": str(encrypt_message(password_2).decode("utf-8") ),
                "email_email_comments": empty_byte_string,
                "password_email_comments": empty_byte_string,
                "email_receive_comments": str(encrypt_message(email_receive_comments).decode("utf-8")),
                }
        with open(secrets_file, 'w') as f:
            json.dump(data, f)
        return False
    return is_open


# REPORT A BUG
@app.callback(
    Output("modal7", "is_open"),
    [Input("report-bug", "n_clicks"), Input("close7", "n_clicks"), Input("send7", "n_clicks"),
     Input('textarea7', 'value')
     ],
    [State("modal7", "is_open")],
)
def report_bug(report_bug_button, close7_button, send_email_developer_button, text, is_open):
    ctx = dash.callback_context
    # print(ctx.triggered)
    interaction_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if interaction_id == "send7":
        send_email_developer(str(text), path_dir+'/loggings.json')
        return False
    elif interaction_id == "report-bug":
        return True
    elif interaction_id == "close7":
        return False

    return is_open


# DEVELOPMENT ENVIRONMENT SWITCH
@app.callback(
    Output('boolean-switch-output', 'children'),
    [Input("test-env-switch", "on")]
)
def change_switch(switch):
    global dev_switch
    if switch == False:
        switch_state = {"state": "False"}
        with open(testenv_file, 'w') as f:
            json.dump(switch_state, f)
        dev_switch = switch_state["state"]
        return "Testenvironment OFF"
    else:
        switch_state = {"state": "True"}
        with open(testenv_file, 'w') as f:
            json.dump(switch_state, f)
        dev_switch = switch_state["state"]
        return "Testenvironment ON"


# LOAD CLIENTS FROM CSV, WORDPRESS OR ELSEWHERE
@app.callback(
    [Output("modal2", "is_open"),
     Output('table-client-info', 'data'),
     Output("loading-1", "children")],
    [Input("login", "n_clicks"),
     Input("close2", "n_clicks"),
     Input('output-container-date-picker-single', 'children'),
     Input('test', 'n_clicks'),
     ],
    [State("modal2", "is_open")],
)
def load_clients(n1, n2, date_picker_output, test, is_open):
    ctx = dash.callback_context
    print(ctx.triggered)
    # print(ctx.triggered)
    interaction_id = ctx.triggered[0]['prop_id'].split('.')[0]

    df_filtered = empty_dataframe()
    print(interaction_id)
    # CREATE EMPTY DATAFRAME AT INITALIZATION
    if not n1 and not n2 and not interaction_id == "test":
        print("first")
        df_filtered = empty_dataframe()
        return is_open, df_filtered.to_dict('records'), ""

    # LOAD TEST SAMPLE IF TEST
    if interaction_id == "test":
        print(date_picker_output)
        df = get_data(date_picker_output)
        print(df.head())
        return is_open, df.to_dict('records'), ""

    # OTHERWISE LOAD CLIENTS LIST AND OPEN MODAL WINDOW
    elif interaction_id == "login":
        print("Do some function to get all the appointments in a dataframe")
        df = get_data(date_picker_output)
        return is_open, df.to_dict('records'), ""

    # CLOSE MODAL WINDWO
    elif interaction_id == "close2":
        is_open = False
        return is_open, df_filtered.to_dict('records'), ""

    # RENEW TABLE AT DATE CHANGE
    elif interaction_id == "output-container-date-picker-single":
        print(date_picker_output)
        df_filtered = get_data(date_picker_output)
        print(df_filtered.head())
        return is_open, df_filtered.to_dict('records'), ""

    else:
        print("end if else statement")
        return is_open, df_filtered.to_dict('records'), ""


# CLIENT SELECTION
@app.callback(Output('table-client-info', 'style_data_conditional'),
              Output('perf_var', 'children'),
              Output('table-client-info', 'active_cell'),
              Output('table-client-info', 'selected_cells'),
              [Input('next', 'n_clicks'),
               Input('previous', 'n_clicks'),
               Input('interval-component', 'n_intervals')],
              Input('table-client-info', 'selected_cells'),
               State('output-container-date-picker-single', 'children'),
              State('table-client-info', 'active_cell'),
              )
def update_table(next, previous, interval, selected_cells, date_picker_output, active_cell):
    ctx = dash.callback_context
    # print(ctx.triggered)
    interaction_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # SET ACTIVE ROW AT INITIALIZATION
    if not active_cell:
        active_row = 0
    else:
        active_row = active_cell["row"]

    # LOG START OF WORK ON CLIENT
    addLogging({'start time': datetime_management.currentTimeUTC(),
                'client number': active_row})  # this will only work if you go forward in the list

    # GET DATAFRAME
    df_new_filtered = read_data()

    # CLICK BUTTON LOGIC
    if interaction_id == "table-client-info":
        # print(selected_cells)
        active_row = int(selected_cells[0]["row"])

        # SET COLOR OF ROW
        color, orga = client_selection.define_color(df_new_filtered, active_row)

        # DO SOME LOGIC
        b = app_connection.select_orga(orga)

    # NEXT BUTTON LOGIC
    elif interaction_id == "next":

        # CREATE BLOCK AT START OF TABLE
        if active_row < len(df_new_filtered):
            active_row += 1
        else:
            active_row = active_row

        # SET COLOR OF ROW
        color, orga = client_selection.define_color(df_new_filtered, active_row)

        # DO SOME LOGIC
        b = app_connection.select_orga(orga)
        if not b: # if logic was unsuccesfull color previous cell
            if active_row < len(df_new_filtered):
                active_row = int(active_row - 1)
                color, orga = client_selection.define_color(df_new_filtered, active_row)

    # PREVIOUS BUTTON LOGIC
    elif interaction_id == "previous":

        # CREATE BLOCK AT START OF TABLE
        if active_row > 0:
            active_row -= 1
        else:
            active_row = active_row

        # SET COLOR OF ROW
        color, orga = client_selection.define_color(df_new_filtered, active_row)

        # DO SOME LOGIC
        b = app_connection.select_orga(orga)
        if not b: # if logic was unsuccesfull color previous cell
            if active_row < len(df_new_filtered):
                active_row = int(active_row + 1)
                color, orga = client_selection.define_color(df_new_filtered, active_row)
    else:
        # if df_new_filtered.isnull().values.any() or (not (len(df_new_filtered))):
        #     color = 'transparent'
        # else:
        color, orga = client_selection.define_color(df_new_filtered, active_row)

    # ADJUST TABLE FORMATTING
    new_style = [
        {
            'if': {
                'filter_query': '{{numeric_date}} < {}'.format(datetime_management.to_integer(dt.now())),
            },
            'backgroundColor': 'grey',
            'color': 'black',
        },
        {
            'if': {
                'row_index': active_row,
            },
            'backgroundColor': color,
            'color': 'white',
        },
        {
            "if": {"state": "selected"},  # 'active' | 'selected'
            "backgroundColor": color,
            "border": "3px light grey",
        },
    ]

    # CALCULATE AVERAGE TIME PER CLIENT
    avg = perf_var_calc()

    # RETURN NEW FORMATTING OT FABLE AND AVERATE TIME PER CLIENT
    return new_style, str(avg) + " minutes per client", {'row': active_row, 'column': 2},[{'row': active_row, 'column': 2}]


# SEND EMAIL WITH TABLE DATA
@app.callback(
    Output("modal3", "is_open"),
    Output("loading-2", "children"),
    [Input("table-client-info", "data"),
     Input("send", "n_clicks"),
     Input("close3", "n_clicks"),
     Input('textarea', 'value')
     ],
    State("modal3", "is_open")
)
def e_mail_comments(data, send, close_button, text, is_open):
    ctx = dash.callback_context
    interaction_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if interaction_id == "send":
        df = pd.DataFrame(data)
        df.to_excel(path_dir+download_excell_filename)
        file = path_dir+download_excell_filename
        # send_email(str(text), file)
        os.remove(file)
        return True, True
    if close_button:
        return False, False
    return is_open, is_open


########################################################################################################################
########################################################################################################################
# THE RUN APPLICATION COMMAND
if __name__ == '__main__':
    if dev_switch==True:
        app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=True)
    else:
        app.run_server(host='0.0.0.0', port=8080, debug=False, use_reloader=True)
