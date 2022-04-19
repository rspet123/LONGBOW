from flask import Flask, request, session, url_for, render_template, redirect

# LONGBOW
# import esipy
from esipy import EsiApp, EsiSecurity, EsiClient
from esipy.exceptions import APIException
from datetime import datetime, timezone
import pickle
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


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/characters')
def characters():
    character_list = db.Characters.find()
    return render_template('characters_fancy.html', character_list=character_list, system_data=system_data)


@app.route('/characters/character_name/<name>')
def character(name):
    # TODO add corp names + caching
    # https://evewho.com/api/corplist/98330748
    character = db.Characters.find_one({"_id": name})
    print(character)
    return render_template('character_fancy.html', character=character, sys_name=sys_name_to_id)


@app.route('/characters/character_id/<id>')
def character_id(id):
    character = db.Characters.find_one({"name": id})
    print(character)
    return render_template('character_fancy.html', character=character, sys_name=sys_name_to_id)


@app.post('/characters/character_name/<name>/comment')
def post_comment(name):
    # TODO add functionality
    comment = request.form['note']
    character = db.Characters.find_one({"_id": name})
    print(character)
    print(type(character))
    # Update Character
    if character["notes"] is None:
        character["notes"] = []
    character["notes"].append(comment)
    # Put it back
    db.Characters.update_one({"_id": character["_id"]}, {"$set": character}, upsert=True)
    return render_template('character_fancy.html', character=character, sys_name=sys_name_to_id)


@app.route('/systems')
def systems():
    system_list = db.Systems.find()
    return render_template('systems.html', system_list=system_list)


# TODO add list of reports to the system page
@app.get('/systems/system/<name>')
def system(name):
    system = db.Systems.find_one({"_id": name})
    reports = character_list = db.SystemReport.find({"system_name": name})
    print(reports)
    drifter_systems = eve_data_tools.get_nearest_drifter_systems(drifters,
                                                                 system_data,
                                                                 sys_name_to_id[system["_id"]]["system_id"],
                                                                 5)

    return render_template('system.html',
                           system=system,
                           drifters=drifter_systems,
                           sys_data=system_data,
                           last_dist=str(5),
                           reports=reports)


@app.post('/systems/system/<name>')
def adjust_system_jumps(name):
    """For adjusting drifter hole jumps"""

    jumps = request.form['drifter_jumps']
    system = db.Systems.find_one({"_id": name})
    reports = character_list = db.SystemReport.find({"system_name": name})
    print(reports)
    drifter_systems = eve_data_tools.get_nearest_drifter_systems(drifters,
                                                                 system_data,
                                                                 sys_name_to_id[system["name"]]["system_id"],
                                                                 int(jumps))
    print(int(jumps))
    return render_template('system.html', system=system,
                           drifters=drifter_systems,
                           sys_data=system_data,
                           last_dist=str(jumps),
                           reports=reports)


@app.route('/report_viewer')
def report_viewer():
    # TODO query db for reports
    reports = db.SystemReport.find()
    return render_template('view_system_reports.html', reports=reports)


@app.route('/report/<id>')
def report(id):
    # TODO query db for reports
    report = db.SystemReport.find_one({"_id": id})
    return render_template('view_report.html', report=report)


@app.route('/targets')
def targets():
    return 'WIP'


@app.get('/system_report')
def system_report():
    """file system report"""
    all_systems = list(sys_name_to_id.keys())
    print(all_systems)
    return render_template('system_report.html', all_systems=all_systems)


@app.post('/system_report')
# https://www.geeksforgeeks.org/autocomplete-input-suggestion-using-python-and-flask/
def post_system_report():
    sys_name = request.form['system']
    chars_in_system = request.form['characters'].splitlines()
    dscan = request.form['dscan']
    print(chars_in_system)
    report = SystemReport(chars_in_system, sys_name, sys_name_to_id[sys_name]["system_id"], datetime.now(timezone.utc))
    report.get_player_ids()
    report.store_report()

    return render_template('view_report.html', report=report.as_json())


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
