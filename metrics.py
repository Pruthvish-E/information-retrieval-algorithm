#imports
import query
import json
import sys


from Elasticsearch.ES import search_snippet
from utils.timer import timer


def metrics(query_string):
  """
  A helper function to obtain performance metrics for the search engine for a particular query.
  Uses the results from elasticsearch as the true labels
  Inputs:
    query_string : The query input of the user
  Outputs:
    confusion_matrix : A tuple of true positive, true negative, false positive and false negative of the results returned by our search engine
  """
  results, happ_time = query.main(query_string)
  #results, happ_time = query.main(query_string)
  es_results, es_time = search_snippet(query_string)
  es_doc_ids = {x['_source']['id'] for x in[i for i in es_results['hits']['hits']]}
  doc_ids = {x['_source']['id'] for x in [i for i in results['hits']]}

  print(happ_time, es_time)
  tp = len(doc_ids.intersection(es_doc_ids))
  fp = len(doc_ids) - tp
  fn = len(es_doc_ids) - tp
  tn = query.ind.ndocs - tp - fp - fn
  confusion_matrix = (tp, fp, fn, tn, happ_time, es_time)
  return confusion_matrix

if __name__ == "__main__":
  assert len(sys.argv) == 2, "Please enter the query to run the search against"
  print(metrics(sys.argv[1]))
