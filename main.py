#!/usr/bin/env python3

from __future__ import print_function

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import os
import json

from dataverse_lib import Dataverse, File
from spark_wordcount import startSpark

#os.environ["coordinates"] = "https://demo.dataverse.org/dataverse/harvard"

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key'
))


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
    if request.args.get('file'):
        session['selected_file'] = request.args.get('file', type=int)
        return redirect(url_for('count'))

    coordinates = os.environ.get("coordinates")
    credentials = os.environ.get("credentials", default="")

    if not coordinates:
        return "Could not find binding to dataverse subtree.<br />Make sure that you have added the secret to this application."

    dataverse = Dataverse(coordinates,credentials)

    dataverse = Dataverse(coordinates,credentials)

    # check for args in URL
    page_num = request.args.get('page', default=1, type=int)
    if page_num < 1:
        page_num = 1

    # list first 10 files from dataverse
    ten_files = dataverse.get_page_of_files(page=page_num)
    #ten_files = [File(x, dataverse, None, json={'name':'File with file_id: '+str(x)}) for x in [11283,11282,11284,11286,11288,11306,11307,11308,11327,11317]]
    
    return render_template('index.html', files=ten_files, page=page_num)

@app.route("/count")
def count():
    if 'selected_file' not in session:
        return redirect(url_for('index'))

    file_id = session['selected_file']

    # download file from dataverse
    coordinates = os.environ.get("coordinates")
    credentials = os.environ.get("credentials", default="")

    if not coordinates:
        return "Could not find binding to dataverse subtree.<br />Make sure that you have added the secret to this application."

    dataverse = Dataverse(coordinates,credentials)

    selected_file = File(file_id, dataverse=dataverse, dataset=None, json=None)
    selected_file.download("data/" + str(file_id) + ".txt")

    # run wordcount
    wordlist = startSpark(get_a_file())
    print(json.dumps(wordlist))

    #wordlist = {"hello":11, "world":2}

    return render_template("count.html", file=selected_file, wordlist=wordlist)

@app.route("/wordcount")
def wordcount():

    final = json.dumps(startSpark(get_a_file()))
    print(final)

    return final


if __name__ == "__main__":
    if not os.path.isdir("data"):
        os.mkdir("data")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)