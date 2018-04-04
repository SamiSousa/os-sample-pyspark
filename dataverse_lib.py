import requests
import sys
try: # python3
	from urllib.request import urlopen
except:
	from urllib2 import urlopen
from pprint import pprint
import json
import shutil
import re

# basic library of commands to run using Dataverse API
class DataverseJson:
	def __init__(self, json):
		self.json = json 
		self.description = json["description"]
		self.name = json["name"]

	def pprint(self):
		# pretty print
		pprint(self.json, indent=2)

	def ToString(self):
		return "Dataverse json Object for " + self.name

class Dataverse(DataverseJson):
	def __init__(self, url, token, json=None):
		if json:
			DataverseJson.__init__(self, json)
		self.url = url
		self.token = token
		# name of server
		self.server = re.match(r"^(https?://.*?\.?.+?\..+?/).+?/.+?$",url).groups()[0] 
		# name of subtree
		self.subtree = url.split("/")[-1] 

	def get_dataverses(self, query="*", per_page=10):
		# returns list of all dataverses in the subtree
		dataverses = []
		dataverse_descriptions = run_iterative_query(self.server + "/api/search/?q=" + query + 
			"&subtree=" + self.subtree + "&type=dataverse", per_page=per_page)

		for dataverse in dataverse_descriptions:
			dataverses.append(Dataverse(dataverse["url"], "", dataverse))

		return dataverses

	def get_datasets(self, query="*", per_page=10):
		# returns list of all datasets in the subtree
		datasets = []
		datasets_descriptions = run_iterative_query(self.server + "/api/search/?q=" + query +
			"&subtree=" + self.subtree + "&type=dataset", per_page=per_page)

		for dataset in datasets_descriptions:
			datasets.append(Dataset(dataset["global_id"], self, json=dataset))

		return datasets

	def get_files(self, query="*", per_page=10):
		# returns list of all files in the subtree
		files = []
		file_descriptions = run_iterative_query(self.server + "/api/search/?q=" + query +
			"&subtree=" + self.subtree + "&type=file", per_page=per_page)

		for file in file_descriptions:
			files.append(File(file["file_id"], self, None, json=file))

		return files

	# get a single file
	def get_file(self, query="*"):
		file_descriptions = run_iterative_query(self.server + "/api/search/?q=" + 
			query + "&subtree=" + self.subtree + "&type=file", limit=1)

		for file in file_descriptions:
			return File(file["file_id"], self, None, json=file)

		# otherwise, no file
		return None
	# toString
	def ToString(self):
		return "Dataverse at url: " + self.url


class Dataset(DataverseJson):
	def __init__(self, global_id, dataverse, json):
		DataverseJson.__init__(self, json)
		self.dataverse = dataverse
		self.global_id = global_id
		self.files = []
		self.get_files(update=True)

	def get_files(self, update=False):
		# return list of files in this dataset
		if self.files and not update:
			# already populated
			return self.files

		native_url = self.dataverse.server + "/api/datasets/:persistentId/versions/:latest-published?persistentId=" + self.global_id

		# create a file based on the native_url given
		dataset = requests.request('GET',native_url).json()

		self.files = []

		for file in dataset["data"]["files"]:
			self.files.append(File(file["dataFile"]["id"], self.dataverse, self))

		return self.files

	def download(self, filename):
		# download files from dataset
		# run a Data Access API call
		access_call = self.dataverse.server + "/api/access/datafiles/"
		for file in self.files:
			access_call += file.file_id
			if file is not files[-1]:
				access_call += ","

		# add the token
		access_call += "?key=" + self.dataverse.token
		
		download_from_url(access_call, filename)

	# toString
	def ToString(self):
		return "Dataset with global_id: " + self.global_id

class File(DataverseJson):
	def __init__(self, file_id, dataverse, dataset, json):
		DataverseJson.__init__(self, json)
		self.dataverse = dataverse
		self.dataset = dataset
		self.file_id = file_id

	def download(self, filename):
		# download file
		# run a Data Access API call
		access_call = self.dataverse.server + "/api/access/datafile/" + self.file_id

		# add the token
		access_call += "?key=" + self.dataverse.token
		
		download_from_url(access_call, filename)

	# toString
	def ToString(self):
		return "File with file_id: " + str(self.file_id)


# utility functions:
def run_query(url):
	# returns a json object of the query response
	return requests.request('GET', url).json()

def run_iterative_query(base_url, start=0, per_page=10, limit=None):
	# returns a list of json objects describing query results
	# base_url is the url to the target dataverse, including query terms, excluding 'start' and 'per_page'
	if limit and limit < start + per_page:
		per_page = limit - start

	query_url = base_url + "&start=" + str(start) + "&per_page=" + str(per_page)

	json_result = run_query(query_url)

	result_list = []

	for item in json_result["data"]["items"]:
		result_list.append(item)

	# check for total_count for this query; base case is query is completed
	total_count = json_result["data"]["total_count"]

	if start + per_page >= total_count:
		return result_list
	if limit and limit >= start + per_page:
		return result_list

	else:
		# continue query
		result_list += run_iterative_query(base_url, start+per_page, per_page, limit)

		return result_list

def download_from_url(url, path):
	# download from url and write to path
	response = urlopen(url).read()
	with open(path, 'wb') as out_file:
		shutil.copyfileobj(response, out_file)
