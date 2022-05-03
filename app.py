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
    """
    It generates a random token, stores it in the session, and then redirects the user to the EVE SSO login page
    :return: The redirect function is being returned.
    """
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
    """
    It finds all the characters in the database and passes them to the template
    :return: A list of all the characters in the database.
    """
    character_list = db.Characters.find()
    return render_template('characters_fancy.html', character_list=character_list, system_data=system_data)


@app.route('/characters/character_name/<name>')
def character(name):
    """
    It takes a character name, looks it up in the database, and renders a template with the character's data

    :param name: The name of the character you want to look up
    :return: A dictionary of the character's information.
    """
    # TODO add corp names + caching
    # https://evewho.com/api/corplist/98330748
    character = db.Characters.find_one({"_id": name})
    print(character)
    return render_template('character_fancy.html', character=character, sys_name=sys_name_to_id)


@app.route('/characters/character_id/<id>')
def character_id(id):
    """
    It takes the name of a character, finds the character in the database, and then renders a template with the character's
    information

    :param id: the name of the character
    :return: A character object
    """
    character = db.Characters.find_one({"name": id})
    print(character)
    return render_template('character_fancy.html', character=character, sys_name=sys_name_to_id)


@app.post('/characters/character_name/<name>/comment')
def post_comment(name):
    """
    It takes a character name, finds the character in the database, adds the comment to the character's notes, and then
    updates the database with the character

    :param name: the name of the character
    :return: A character object
    """
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
    """
    It finds all the systems in the database and passes them to the template
    :return: The systems.html template is being returned.
    """
    system_list = db.Systems.find()
    return render_template('systems.html', system_list=system_list)


# TODO add list of reports to the system page
@app.get('/systems/system/<name>')
def system(name):
    """
    It takes a system name, finds the system in the database, finds all reports for that system, finds the nearest drifter
    systems, and then renders the system.html template with all of that data

    :param name: The name of the system to display
    :return: The system.html template is being returned.
    """
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
                           reports=reports,
                           name_data=sys_name_to_id)


@app.post('/systems/system/<name>')
def adjust_system_jumps(name):
    """
    It takes a system name, finds the system in the database, finds the reports for that system, finds the nearest drifter
    systems, and renders the system.html template with the system, drifter systems, system data, last distance, reports, and
    name data

    :param name: The name of the system you want to look up
    :return: The system.html template is being returned.
    """
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
                           reports=reports,
                           name_data=sys_name_to_id)


@app.route('/report_viewer')
def report_viewer():
    """
    It queries the database for all system reports, and then renders the view_system_reports.html template, passing in the
    reports variable.
    :return: A list of reports
    """
    reports = db.SystemReport.find()
    return render_template('view_system_reports.html', reports=reports)


@app.route('/report/<id>')
def report(id):
    """
    It queries the database for a report with the given id, and then renders a template with the report

    :param id: the id of the report to be viewed
    :return: A report object
    """
    report = db.SystemReport.find_one({"_id": id})
    return render_template('view_report.html', report=report)


@app.route('/targets')
def targets():
    return 'WIP'


@app.get('/system_report')
def system_report():
    """
    The function system_report() returns a rendered template called system_report.html, which is a list of all the systems
    in the system_name_to_id dictionary.
    :return: The system_report.html file is being returned.
    """
    """file system report"""
    all_systems = list(sys_name_to_id.keys())
    print(all_systems)
    return render_template('system_report.html', all_systems=all_systems)


@app.post('/system_report')
def post_system_report():
    """
    It takes the form data from the web page, creates a `SystemReport` object, gets the player IDs from the API, and then
    stores the report in the database
    :return: A JSON object containing the report data.
    """
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
    """
    It takes the current system ID from the character's location, then uses the `eve_data_tools` module to get the nearest
    drifter systems, and returns the output
    :return: A list of the nearest drifter systems to the current system.
    """
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
    """
    It takes the code and state parameters from the URL, checks that the state parameter matches the session token, and then
    uses the code parameter to get an access token from the EVE Online SSO
    :return: The character data is being returned.
    """
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
    app.run(host="0.0.0.0", port=8080)
