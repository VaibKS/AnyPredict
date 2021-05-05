import os
import json
from flask import Flask, session, request, send_file
from flask_cors import CORS, cross_origin
from db.auth import signIn
from db import registerUser

from ml import linear_regression
from werkzeug.utils import secure_filename

UPLOADS_FOLDER = "uploads"

app = Flask(__name__)
cors = CORS(app)

app.secret_key = os.environ["SECRET_KEY"]
app.config["UPLOAD_FOLDER"] = UPLOADS_FOLDER


@app.route("/")
def hello_world():
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post action="data/upload" enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <form method="POST" action="auth/sign-in">
        <h1>Log In</h1>
        <input type=text name=email>
        <input type=text name=password>
      <input type=submit value=Submit>
    </form>
    <form method="POST" action="auth/register">
        <h1>Register</h1>
        <input type=text name=name>
        <input type=text name=email>
        <input type=text name=password>
      <input type=submit value=Submit>
    </form>
    <h1>Links</h1>
    <a href="auth/session">Session</a>
    <a href="ml/train">Train</a>
    <a href="ml/output.csv">Download</a>
    """


@app.route("/auth/sign-in", methods=["POST"])
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


@app.route("/auth/register", methods=["POST"])
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


@app.route("/auth/session", methods=["GET"])
def get_session():
    if "user" in session:
        return json.dumps(session["user"])
    return json.dumps({"status": "unauthenticated"})


@app.route("/auth/logout", methods=["GET", "POST"])
def logout():
    session.pop("user", None)
    return json.dumps({"status": "invalid"})


@app.route("/data/upload", methods=["GET", "POST"])
def handleFileUpload():
    if "user" in session:
        email = session["user"]["email"]
        localpath = "{}/{}".format(UPLOADS_FOLDER, email)
        # check directory
        if not os.path.isdir(localpath):
            os.mkdir(localpath)

        if "file" not in request.files:
            return json.dumps({"status": "error"})
        file = request.files["file"]
        print("Saving")
        file.save("{}/dataset_train.csv".format(localpath))
        return json.dumps({"status": "uploaded"})
    else:
        return json.dumps({"status": "unauthenticated"})


@app.route("/ml/train", methods=["GET"])
def train_model():
    if "user" in session:
        email = session["user"]["email"]
        folderpath = "{}/{}".format(UPLOADS_FOLDER, email)
        if os.path.isfile(folderpath + "/dataset_train.csv"):
            linear_regression(email)
            return json.dumps({"status": "complete"})
        else:
            return json.dumps({"status": "no_files"})
    else:
        return json.dumps({"status": "unauthorized"})


@app.route("/ml/output.csv", methods=["GET"])
def get_output():
    if "user" in session:
        email = session["user"]["email"]
        filepath = "{}/{}/output.csv".format(UPLOADS_FOLDER, email)
        if os.path.isfile(filepath):
            return send_file(filepath, mimetype="text/csv")
        else:
            return json.dumps({"status": "error"})
    else:
        return json.dumps({"status": "unauthorized"})
