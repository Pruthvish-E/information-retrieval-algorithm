import pandas as pd
import requests
from elasticsearch import helpers, Elasticsearch
import csv
import json
import sys
from pprint import pprint
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from utils.timer import timer_decorator, timer
from config import config_params
from preprocess import preprocess_sentence
from tqdm import tqdm

# make sure ES is up and running
# res = requests.get('http://localhost:9200')

def generate_actions(path):
    """
    Reads csv through csv.DictReader() and yields a single document for each record.
    This function is passed into the bulk() helper to create many documents in sequence.
    """
    uid = 0
    for _csv in tqdm(sorted(os.listdir(path))):
        file = os.path.join(path, _csv)
        with open(file, mode = "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc = {
                     "id" : uid,
                     "document_name" : _csv,
                     # "URL" : row["\ufeffURL"],
                     # "MatchDateTime" : row["MatchDateTime"],
                     "Station" : row["Station"],
                     "Show" : row["Show"],
                     # "IAShowID" : row["IAShowID"],
                     # "IAPreviewThumb" : row["IAPreviewThumb"],
                     "Snippet" : " ".join(preprocess_sentence(row["Snippet"])) if config_params["es_preprocess"] else row['Snippet']
                }
                uid += 1
                yield doc

def build_index(es, index, path):
    """ builds ES index """
    if index not in cat_indices():
        successes = 0
        for ok, action in helpers.streaming_bulk(es, index=index, actions=generate_actions(path),):
            successes += ok
        print("Indexed %d documents" % (successes))

def delete_index(es, index):
    """ deletes ES index """
    try:
        if "." not in index:
            es.indices.delete(index=index)
            print("Successfully deleted", index)
    except Exception as error:
        print("indices.delete.error", error)

def cat_indices():
    """ lists ES indices """
    indices = es.indices.get_alias().keys()
    return list(sorted(indices))

@timer_decorator
def search(search):
    res = es.search(index=config_params['es_index'], body=search)
    return res

@timer
def search_snippet(query):
    search_object = {
        "size" : config_params["result_size"],
        "query": {
            "multi_match": {
                "query" : query,
                "fields" : ["Snippet"]
            }
        }
    }
    res = search(json.dumps(search_object))
    return res

es = Elasticsearch([{'host': config_params['es_host'], 'port': config_params['es_port']}])

if __name__ == '__main__':
    # connect to our cluster
    if es is not None:
            path = "TelevisionNews/"
            index = config_params["es_index"]

            delete_index(es, index)
            build_index(es, index, path)

            # TODO - need to add types of queries
            # search_object = {"size": 10000, query": {"match_all": {}}}
            # search_object = {
            #     "size" : 20,
            #     "query": {
            #         "multi_match": {
            #             "query" : "brazil's government is defending its plan to build dozens of huge hydro-electric dams",
            #             "fields" : ["Snippet"]
            #         }
            #     }
            # }
            # res = search(json.dumps(search_object))

            query = "brazil's government is defending its plan to build dozens of huge hydro-electric dams"
            res = search_snippet(query)
            print(json.dumps(res, indent = 3))
