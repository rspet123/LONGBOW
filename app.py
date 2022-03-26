from flask import Flask, request, session, url_for, render_template, redirect

# import esipy
from esipy import EsiApp, EsiSecurity, EsiClient
from esipy.exceptions import APIException
# import pickle
import configparser
import random
import hmac
import hashlib
import eve_data_tools

# https://zkillboard.com/api/kills/characterID/447073625/


# Init ESI stuff
config = configparser.ConfigParser()
config.read("config.ini")
CLIENT_ID = config.get('ESI', 'CLIENT_ID')
SECRET_KEY = config.get('ESI', 'SECRET_KEY')
CALLBACK = config.get('ESI', 'CALLBACK')
USER_AGENT = config.get('ESI', 'USER_AGENT')


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

#Generate our ESI tools
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
def hello_world():
    return 'WIP'


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
        return str(system_id)
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
    print(character_data)
    data_store["character_data"] = character_data

    return redirect(url_for("stats"))


if __name__ == '__main__':
    app.run()
