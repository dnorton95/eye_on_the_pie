from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'flask_app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.secret_key = "Secret secret tunnel"
