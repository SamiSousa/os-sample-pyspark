#!/usr/bin/env python3

# Spark Reference: https://stackoverflow.com/a/32845282

from __future__ import print_function
import re, sys
from pyspark import SparkContext, SparkConf

def linesToWordsFunc(line):
    wordsList = line.split()
    wordsList = [re.sub(r'\W+', '', word) for word in wordsList]
    filtered = filter(lambda word: re.match(r'\w+', word), wordsList)
    return filtered

def wordsToPairsFunc(word):
    return (word, 1)

def reduceToCount(a, b):
    return (a + b)

def startSpark(filename):
    # provide a valid filename and run wordcount on it

    dicto = {}

    conf = SparkConf().setAppName("Words count").setMaster("local")
    sc = SparkContext(conf=conf)

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

