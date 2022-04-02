from flask import Flask, request, session, url_for, render_template, redirect

# LONGBOW
# import esipy
from esipy import EsiApp, EsiSecurity, EsiClient
from esipy.exceptions import APIException
from datetime import datetime, timezone
# import pickle
import configparser
import random
import hmac
import hashlib
import eve_data_tools
import db
from Player import Player
from SystemReport import SystemReport

# https://zkillboard.com/api/kills/characterID/447073625/


# Init ESI stuff
config = configparser.ConfigParser()
config.read("config.ini")
CLIENT_ID = config.get('ESI', 'CLIENT_ID')
SECRET_KEY = config.get('ESI', 'SECRET_KEY')
CALLBACK = config.get('ESI', 'CALLBACK')
USER_AGENT = config.get('ESI', 'USER_AGENT')

system_data = eve_data_tools.get_system_data()
system_data = eve_data_tools.get_system_jumps(system_data)
drifters = eve_data_tools.get_possible_drifter_systems()
sys_name_to_id = eve_data_tools.get_system_data_by_name()


def generate_token():
    """Generate OAuth token"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    rand = random.SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(40))
    out = hmac.new(
        SECRET_KEY.encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return out


# Generate our ESI tools
esiapp = EsiApp().get_latest_swagger

esisecurity = EsiSecurity(
    redirect_uri=CALLBACK,
    client_id=CLIENT_ID,
    secret_key=SECRET_KEY,
    headers={'User-Agent': USER_AGENT}
)

esiclient = EsiClient(
    security=esisecurity,
    cache=None,
    headers={'User-Agent': USER_AGENT}
)

# Flask Routes
app = Flask(__name__)
app.secret_key = generate_token()

data_store = {}


@app.route('/sso/login')
def login():
    """ this redirects the user to the EVE SSO login """
    token = generate_token()
    session['token'] = token
    return redirect(esisecurity.get_auth_uri(
        state=token,
        scopes=['esi-location.read_location.v1']
    ))


@app.route('/')
def index():
    return render_template('menu.html')


# TODO I NEED HTML FOR ALL THIS UGH
# https://stackoverflow.com/questions/11124940/creating-link-to-an-url-of-flask-app-in-jinja2-template

@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/characters')
def characters():
    character_list = db.Characters.find()
    out = ""
    for char in character_list:
        print(char["_id"])
        out = out + char["_id"]
    return render_template('characters.html')

@app.route('/characters/character/<name>')
def character(name):
    # TODO add functionality
    character = db.Characters.find_one({"_id":name})
    print(character)
    return render_template('character.html',character = character)

@app.route('/systems')
def systems():
    # TODO query db for systems
    return render_template('systems.html')


@app.route('/report_viewer')
def report_viewer():
    # TODO query db for reports
    return render_template('view_system_reports.html')


@app.route('/targets')
def targets():
    return 'WIP'


@app.get('/system_report')
def system_report():
    return render_template('system_report.html')


@app.post('/system_report')
def post_system_report():
    sys_name = request.form['system']
    chars_in_system = request.form['characters'].splitlines()
    dscan = request.form['dscan']
    print(chars_in_system)
    report = SystemReport(chars_in_system, sys_name, sys_name_to_id[sys_name]["system_id"], datetime.now(timezone.utc))
    report.get_player_ids()
    report.store_report()
    near_drifters = eve_data_tools.get_nearest_drifter_systems(drifters, system_data,
                                                               sys_name_to_id[sys_name]["system_id"], 5)
    out = ""
    for drifter in near_drifters:
        out += system_data[drifter]["name"] + ", "
    return out


@app.get('/stats')
def stats():
    """Shows Stats for the current system, WIP"""
    # get_characters_character_id_location
    if data_store.get("character_data", False):
        character_data = data_store["character_data"]
        char_id = character_data["sub"].split(':')[2]
        op = esiapp.op['get_characters_character_id_location'](
            character_id=char_id
        )
        location = esiclient.request(op)
        print(str(location.data))
        system_id = location.data.solar_system_id
        output = eve_data_tools.get_nearest_drifter_systems(drifters, system_data, str(system_id), 5)
        return str(output)
    else:
        return redirect(url_for("login"))


@app.route('/sso/callback')
def callback():
    code = request.args.get('code')
    token = request.args.get('state')
    sess_token = session.pop('token', None)
    print(code)
    if sess_token is None or token is None or token != sess_token:
        return 'Login EVE Online SSO failed: Session Token Mismatch', 403
    try:
        auth_response = esisecurity.auth(code)
    except APIException as e:
        return 'Login EVE Online SSO failed: %s' % e, 403
    character_data = esisecurity.verify()
    data_store["character_data"] = character_data

    return redirect(url_for("stats"))


if __name__ == '__main__':
    app.run()
