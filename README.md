# os-sample-pyspark
A quick Apache Spark application for OpenShift in Python

This readme is based off of [radanalytics.io](https://radanalytics.io)'s [tutorial-sparkpi-python-flask](https://github.com/radanalyticsio/tutorial-sparkpi-python-flask) project

It is intended to be
used as a source-to-image application.

## Quick start

You should have access to an OpenShift cluster and be logged in with the
`oc` command line tool.

1. Create the necessary infrastructure objects
   ```bash
   oc create -f https://radanalytics.io/resources.yaml
   ```

2. Launch sparkpi
   ```bash
   oc new-app --template oshinko-python-build-dc  \
       -p APPLICATION_NAME=pyspark \
       -p GIT_URI=https://github.com/SamiSousa/os-sample-pyspark
   ```

3. Expose an external route
   ```bash
   oc expose svc/pyspark
   ```

4. Visit the exposed URL with your browser or other HTTP tool, for example:
   ```bash
   $ curl http://`oc get routes/pyspark --template='{{.spec.host}}'`
   Python Flask Spark server running. Add the 'main' route to this URL to invoke the app.

   $ curl http://`oc get routes/pyspark --template='{{.spec.host}}'`/main
   (something from wordcount)
   ```
