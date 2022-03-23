from flask import Flask
import esipy
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/sso/callback/<id>')
def callback(id):
    return id


if __name__ == '__main__':
    app.run()
