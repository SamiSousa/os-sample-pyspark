#!/usr/bin/env python3

# Flask reference: https://github.com/radanalyticsio/tutorial-sparkpi-python-flask

from __future__ import print_function

from flask import Flask, request
import os
import json

from dataverse_lib import Dataverse
#from spark_wordcount import startSpark

os.environ["coordinates"] = "https://demo.dataverse.org/dataverse/harvard"

app = Flask(__name__)

def get_a_file():
    # return filename of a downloaded file
    coordinates = str(os.environ["coordinates"])

    # get a dataverse
    dataverse = Dataverse(coordinates, "")

    # get file from dataverse
    file = dataverse.get_file()

    # download file
    filename = "data/" + str(file.file_id) + ".txt"
    file.download(filename)

    return filename

@app.route("/")
def index():
    coordinates = str(os.environ["coordinates"])
    #credentials = os.environ["credentials"]
    message = ("Python Flask Spark server running. Add the 'wordcount' route to this URL to invoke the app." +
        "\ncoordinates=" + coordinates +
        "\ncredentials=<redacted>")
    return message

@app.route("/files")
def service_files():
    dataverse = Dataverse(os.environ["coordinates"], "")
    files = dataverse.get_files(limit=10)
    response = ""
    for file in files:
        response += "<div>" + str(file.json) + "</div>"
    return response

@app.route("/datasets")
def service_datasets():
    dataverse = Dataverse(os.environ["coordinates"], "")
    datasets = dataverse.get_datasets(limit=10)
    response = ""
    for dataset in datasets:
        response += "<div>" + str(dataset.json) + "</div>"
    return response

'''
@app.route("/datasets/<global_id>")
def files_from_dataset(global_id):
    dataverse = Dataverse(os.environ["coordinates"], "")
    dataset = Dataset(global_id, dataverse, json=None)
    response = ""
    for file in dataset.get_files():
        response += "<div>" + str(file.json) + "</div>"
    return response
'''

@app.route("/dataverses")
def service_dataverses():
    dataverse = Dataverse(os.environ["coordinates"], "")
    dataverses = dataverse.get_dataverses(limit=10)
    response = ""
    for subtree in dataverses:
        response += "<div>" + str(subtree.json) + "</div>"
    return response

'''
@app.route("/wordcount")
def wordcount():

    final = json.dumps(startSpark(get_a_file()))
    print(final)

    return final
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)