import os
import json
from flask import Flask, session, request, send_file, render_template
from flask_cors import CORS, cross_origin
from db.auth import signIn
from db import registerUser

from ml import linear_regression
from werkzeug.utils import secure_filename

import pyAesCrypt

from os import stat

bufferSize = 64 * 1024
password = "q3t6w9z_C"


def decrypt_file(aes_filepath, csv_filepath):
    try:
        pyAesCrypt.decryptFile(aes_filepath, csv_filepath, password, bufferSize)
        return True
    except:
        return False


def encrypt_file(csv_filepath, aes_filepath):
    try:
        pyAesCrypt.encryptFile(csv_filepath, aes_filepath, password, bufferSize)
        return True
    except:
        return False


UPLOADS_FOLDER = "uploads"

app = Flask(__name__)
cors = CORS(app)

app.secret_key = os.environ["SECRET_KEY"]
app.config["UPLOAD_FOLDER"] = UPLOADS_FOLDER

if not os.path.isdir("uploads"):
    os.mkdir("uploads")


@app.route("/")
def hello_world():
    return render_template("index.html")


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

        aes_filepath = "{}/dataset.csv.aes".format(localpath)
        csv_filepath = "{}/dataset.csv".format(localpath)

        file.save(aes_filepath)

        if decrypt_file(aes_filepath, csv_filepath):
            os.remove(aes_filepath)
            return json.dumps({"status": "uploaded"})
        else:
            os.remove(aes_filepath)
            return json.dumps({"status": "decrypt-error"})
    else:
        return json.dumps({"status": "unauthenticated"})


@app.route("/data/dataset.csv", methods=["GET"])
def get_dataset():
    if "user" in session:
        email = session["user"]["email"]
        filepath = "{}/{}/dataset.csv".format(UPLOADS_FOLDER, email)
        if os.path.isfile(filepath):
            return send_file(filepath, mimetype="text/csv")
        else:
            return json.dumps({"status": "error"})
    else:
        return json.dumps({"status": "unauthorized"})


@app.route("/ml/train", methods=["GET"])
def train_model():
    if "user" in session:
        email = session["user"]["email"]
        folderpath = "{}/{}".format(UPLOADS_FOLDER, email)
        csv_path = folderpath + "/dataset.csv"
        output_path = folderpath + "/output.csv"
        aes_path = folderpath + "/output.csv.aes"
        if os.path.isfile(csv_path):
            is_success = linear_regression(email)
            encrypt_file(output_path, aes_path)
            return (
                json.dumps({"status": "complete"})
                if is_success
                else json.dumps({"status": "error"})
            )
        else:
            return json.dumps({"status": "no_files"})
    else:
        return json.dumps({"status": "unauthorized"})


@app.route("/ml/output.csv.aes", methods=["GET"])
def get_output_aes():
    if "user" in session:
        email = session["user"]["email"]
        filepath = "{}/{}/output.csv.aes".format(UPLOADS_FOLDER, email)
        if os.path.isfile(filepath):
            return send_file(filepath, mimetype="application/octet-stream")
        else:
            return json.dumps({"status": "error"})
    else:
        return json.dumps({"status": "unauthorized"})


@app.route("/ml/output.csv", methods=["GET"])
def get_output_csv():
    if "user" in session:
        email = session["user"]["email"]
        filepath = "{}/{}/output.csv".format(UPLOADS_FOLDER, email)
        if os.path.isfile(filepath):
            return send_file(filepath, mimetype="application/octet-stream")
        else:
            return json.dumps({"status": "error"})
    else:
        return json.dumps({"status": "unauthorized"})
