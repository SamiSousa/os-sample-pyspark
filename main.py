#!/usr/bin/env python3

# Flask reference: https://github.com/radanalyticsio/tutorial-sparkpi-python-flask

from __future__ import print_function

from flask import Flask, request
import os
import json

from dataverse_lib import Dataverse

app = Flask(__name__)

def get_a_file():
    # return filename of a downloaded file
    coordinates = str(os.environ["coordinates"])

    # get a dataverse
    dataverse = Dataverse(coordinates, "")

    # get file from dataverse
    file = dataverse.get_file()

    # download file
    filename = str(file.file_id) + ".txt"
    file.download(filename)

    return filename

@app.route("/")
def init():
    coordinates = str(os.environ["coordinates"])
    #credentials = os.environ["credentials"]
    message = ("Python Flask Spark server running. Add the 'wordcount' route to this URL to invoke the app." +
        "\ncoordinates=" + coordinates +
        "\ncredentials=<redacted>")
    return message

@app.route("/wordcount")
def wordcount():

    final = json.dumps(main(get_a_file()))
    print(final)

    return final

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)