from flask import Flask
import esipy
import pickle
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.INI")
CLIENT_ID = config.get('ESI','CLIENT_ID')
SECRET_KEY = config.get('ESI','SECRET_KEY')
CALLBACK = config.get('ESI','CALLBACK')
@app.route('/e')
def e():
    return 'Hello World!'

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.get('/stats')
def stats():
    return 'Hello World!'

@app.route('/sso/callback/<id>')
def callback(id):
    return id


if __name__ == '__main__':
    app.run()
