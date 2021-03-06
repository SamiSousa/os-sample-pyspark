# sample-dataverse-app

An Apache Spark application for OpenShift using Pyspark and Flask that binds to services provided by [dataverse-broker](https://github.com/dataverse-broker/dataverse-broker).

This project uses OpenShift's source-to-image tool.

## Quick start

You should have access to an OpenShift cluster and be logged in with the
`oc` command line tool. 

1. Select a Dataverse service from OpenShift's Service Catalog, and create a secret. If dataverse services aren't listed, contact your cluster admin. Or, if deploying to a local cluster, follow the instructions at the [dataverse-broker](https://github.com/dataverse-broker/dataverse-broker) project.

2. Make sure you're inside a project
   - To display a list of all the projects-
      ```bash
      $ oc get projects
      ```
   - Select one of the projects-
      ```bash
      $ oc project myproject
      ```

3. Create the necessary infrastructure objects
   ```bash
   oc create -f https://radanalytics.io/resources.yaml
   ```

4. Launch spark app
   ```bash
   oc new-app --template oshinko-python-spark-build-dc  \
       -p APPLICATION_NAME=pyspark \
       -p GIT_URI=https://github.com/dataverse-broker/sample-dataverse-app
   ```

5. Add the secret created in step 1 to the pyspark application
   - Go to the Overview section of your project
   - Go to the Dataverse service you chose in the 1st step, click on `View Secret`
   - Click on `Add to Application` to add the secret to the `pyspark` application

6. Expose an external route
   ```bash
   oc expose svc/pyspark
   ```

7. Visit the exposed URL with your browser or other HTTP tool, and be prompted by the web UI
   - Enter the following if the application is not yet available on the browser-
      ```bash
      $ oc get pods
      ```
   - Select one of the running pods (for example: pyspark-2-vf59x) from the output to view its logs and see if the application is still waiting for the cluster to be available-
      ```bash
      $ oc logs -f pyspark-2-vf59x
      ```

## Common Issues

#### :warning:The application is timing out on some files

Some users may experience this issue because the flask application waits on the spark cluster to complete it's computation before it displays the wordcount result webpage. This can be caused by:

- The file chosen is very large and as a result the browser timesout before the spark cluster completes the calculation.

- The spark cluster is starved for resources (see ["My spark cluster keeps restarting"](#My-spark-cluster-keeps-restarting))

#### :warning:My spark cluster keeps restarting

This is can occur when:

- The spark cluster doesn't have enough resources, such as cpu or memory. Try adjusting the limits set on your spark worker (it has a 'w' in it's name) so that it has at least 1 GiB of Memory.

#### :warning:The application returns an "Internal Server Error"

This can occur when:

- The file selected is not a text-file (perhaps some binary format like .pdf)

- The flask app crashes for any reason, perhaps a bug. [Post an issue](https://github.com/dataverse-broker/sample-dataverse-app/issues/new) so we can help sort it out.

## Explanation of certain items

The [`requirements.txt`](https://github.com/dataverse-broker/sample-dataverse-app/blob/master/requirements.txt) file contains required packages needed for this python application.

The [`.s2i`](https://github.com/dataverse-broker/sample-dataverse-app/tree/master/.s2i) folder contains the environment variables for our main script which is added to the source image that is generated by radanalytics.io / Oshinko

The [`dataverse_lib.py`](https://github.com/dataverse-broker/sample-dataverse-app/blob/master/dataverse_lib.py) script contains the functions for interacting with the [`Dataverse API`](http://guides.dataverse.org/en/latest/api/), such as searching and downloading certain files within a dataverse, or a dataverse subtree.

The [`spark_wordcount.py`](https://github.com/dataverse-broker/sample-dataverse-app/blob/master/spark_wordcount.py) script contains the logic for running the `Spark` word count file on a txt file.

The [`main.py`](https://github.com/dataverse-broker/sample-dataverse-app/blob/master/main.py) script contains a `Flask` application which allows you to select a file from the Dataverse service to run through wordcount, and displays the results.


## Credits

This project is based off of [radanalytics.io](https://radanalytics.io)'s [tutorial-sparkpi-python-flask](https://github.com/radanalyticsio/tutorial-sparkpi-python-flask) project.

The [`spark_wordcount.py`](https://github.com/dataverse-broker/sample-dataverse-app/blob/master/spark_wordcount.py) spark application is borrowed from [this StackOverflow answer](https://stackoverflow.com/a/32845282).

Calls to dataverse follow a mix of Search API, Data Access API, and Native API calls to Dataverse as documented [here](http://guides.dataverse.org/en/latest/api/).
