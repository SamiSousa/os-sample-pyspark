#!/usr/bin/env python3

# Reference: https://stackoverflow.com/a/32845282

from __future__ import print_function
import re, sys
from pyspark import SparkContext, SparkConf

from flask import Flask, request
import os
import json

from dataverse_lib import Dataverse

app = Flask(__name__)

def linesToWordsFunc(line):
    wordsList = line.split()
    wordsList = [re.sub(r'\W+', '', word) for word in wordsList]
    filtered = filter(lambda word: re.match(r'\w+', word), wordsList)
    return filtered

def wordsToPairsFunc(word):
    return (word, 1)

def reduceToCount(a, b):
    return (a + b)

def main():

    dicto = {}

    conf = SparkConf().setAppName("Words count").setMaster("local")
    sc = SparkContext(conf=conf)
 
    # get file from dataverse
    filename = get_a_file()

    rdd = sc.textFile(filename)

    words = rdd.flatMap(linesToWordsFunc)
    pairs = words.map(wordsToPairsFunc)
    counts = pairs.reduceByKey(reduceToCount)

    # Get the first top 100 words
    output = counts.takeOrdered(100, lambda (k, v): -v)

    for(word, count) in output:
        # print to stderr so we can see it in the pod's logs (maybe?)
        print( word, ':', str(count), file=sys.stderr)

        dicto.update({ word : str(count) })

    sc.stop()
    return dicto

def get_a_file():

    coordinates = str(os.environ["coordinates"])

    # get a dataverse
    dataverse = Dataverse(coordinates, "")

    # get file from dataverse
    file = dataverse.get_file()

    # download file
    filename = str(file.fileid) + ".txt"
    file.download(filename)

    return filename

@app.route("/")
def init():
    coordinates = str(os.environ["coordinates"])
    #credentials = os.environ["credentials"]
    message = ("Python Flask Spark server running. Add the 'main' route to this URL to invoke the app." +
        "\ncoordinates=" + coordinates +
        "\ncredentials=<redacted>")
    return message

@app.route("/main")
def wordcount():

    final = json.dumps(main())
    print(final)

    return final

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)