import os
import json
from flask import Flask, session, request
from db.auth import signIn
from db import registerUser

from ml import linear_regression 

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route("/")
def hello_world():
    return "AnyPredict: running"


@app.route("/api/sign-in", methods=["POST"])
def signInAPI():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        res = signIn(email, password)

        if not res:
            return json.dumps({"state": "invalid"})
        res["state"] = "valid"
        return json.dumps(res)

    else:
        return render_template("status/400.html"), 400


@app.route("/api/register", methods=["POST"])
def registerAPI():
    if request.method == "POST":

        user = {
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"],
        }

        return json.dumps(registerUser(user))

    else:
        return render_template("status/400.html"), 400

@app.route('/api/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return json.dumps({'status': 'invalid'})

@app.route("/upload_train", methods=['POST'])
def handleFileUpload():
    if 'file' in request.files:
        dataset = request.files['file']
        if dataset.filename != '':
            dataset.save(os.path.join(app.config['UPLOAD_FOLDER'], 'dataset_train.csv'))
            return "File upload successful"
    return "File upload failed"

@app.route("/upload_test", methods=['POST'])
def handleFileUpload2():
    if 'file' in request.files:
        dataset = request.files['file']
        if dataset.filename != '':
            dataset.save(os.path.join(app.config['UPLOAD_FOLDER'], 'dataset_test.csv'))
            return "File upload successful"
    return "File upload failed"
