#imports
import pickle
import indexes
import json
import os
import datetime
import pandas as pd


from utils.timer import timer_decorator, timer
from collections import defaultdict
from config import config_params


ind = None

#load pickle file to retrieve preprocessed corpus
with open(os.path.join('data', 'data.pkl'), "rb") as f:
    data_dict = pickle.load(f)


def preprocess_query(query):
  """
  This function extracts the required document name and/or the station and show name from the user query
  Inputs:
    query : The query string input by the user
  Outputs:
    query : The query stripped of the document name and station name
    filters : A dictionary consisting of the document name , the station name, the show name
  """
  query = query.strip()
  channel = None
  show = None
  filters = {}

  if '<' in query:
    #extract doc
    bt1 = query.index('<')
    bt2 = query.index('>')
    filters['document'] = query[bt1+1:bt2]
    query = query[bt2+1:]
  else:
    filters['document'] = None

  if '`' in query:
    #extract the field
    bt1 = query.index('`')
    bt2 = query.index('`', query.index('`')+1)
    filters['channel'] = query[bt1+1:bt2]

    if '/' in filters['channel']:
      filters['channel'], filters['show'] = filters['channel'].split('/')

    #strip the channel condition from the query
    query = query[bt2+1:]
  return query, filters



def postprocess_query(docs,scores, filters):
  """
  This function filters the results which match the station and show mentioned by the user
  Inputs:
    docs : The matching snippets' ids for the query
    scores : The scores of the snippets returned
    filters : A dictionary consisting of the document name , the station name, the show name
  Outputs:
    docs : The snippets' ids which match the station name and show name
    scores : The scores of the snippets which match the station name and show name
  """
  result = []
  score=[]

  if len(filters)==0:
    return docs, scores
  
  #postprocess the docs and maintain only the ones with the given show/channel
  for i in range(len(docs)):
    if ('channel' not in filters or len(filters['channel'])==0 or data_dict['rowdict'][docs[i]][2] == filters['channel']) and \
      ('show' not in filters or len(filters['show'])==0 or data_dict['rowdict'][docs[i]][3] == filters['show']) :

      result.append(docs[i])
      if(config_params['index']==1):
        score.append(scores[i])
  
  return result,scores


def prepare_query(query):
  """
  This function sets the required snippets for query and also the type of index to be used
  Inputs:
    query : The query string input by the user
  Outputs:
    The output returned by the perform_query function.
  """
  global ind
  #load the processed pickle file
  with open(os.path.join("data", "data.pkl"), "rb") as f:
    data_dict = pickle.load(f)

  new_rowterm_dict={}
  query, filters = preprocess_query(query)
  if filters['document'] is not None:
    for j in data_dict['rowterms']:
      if data_dict['rowdict'][j][1][:-4] == filters['document']:
        new_rowterm_dict[j]=data_dict['rowterms'][j]
  else:
    new_rowterm_dict=data_dict['rowterms']

  if ind is None:
    if config_params["index"] == 1:
      ind = indexes.TFIDFIndex(new_rowterm_dict)
    elif config_params["index"] == 2:
      ind=indexes.BooleanQuery(new_rowterm_dict)
    elif config_params['index'] == 3:
      ind =indexes.PositionalIndex(new_rowterm_dict)

  return perform_query(new_rowterm_dict,query, filters)



@timer_decorator
def perform_query(new_rowterm_dict,query, filters):
  """
  This function performs the query on the user query string and returns the relevant snippets
  Inputs:
    new_rowterm_dict : A dictionary that has the mapping of the snippet ids and the terms of the snippets
    query : the query string of the user
    filters : A dictionary consisting of the document name , the station name, the show name
  Outputs:
    new_rowterm_dict : A dictionary that has the mapping of the snippet ids and the terms of the snippets
    docs : The snippets' ids which match the station name and show name
    scores : The scores of the snippets which match the station name and show name
  """
  docs = ind.query(query)
  if config_params['index']==1:
    scores=[i[1] for i in docs]
    docs=[i[0] for i in docs]
  else:
    scores=[]
  docs, scores = postprocess_query(docs, scores, filters)
  return new_rowterm_dict, docs, scores


@timer
def main(query):
  """
  This function formats the returned results in a similar format to the elastic serach's return format
  Input:
    The query string of the user
  Output:
    json_res : A dictionary which has the output 
  """
  d_dict, docs, scores = prepare_query(query)

  json_res={}
  if config_params['index']==1:
    json_res['index']="vector space model(tf idf)"
  elif config_params['index']==2:
    json_res['index']="boolean query"
  elif config_params['index']==3:
    json_res['index']="positional index"


  if config_params['stopword_removal']==1:
    json_res['stopword_removal']=True
  else:
    json_res['stopword_removal']=False
  if config_params['preprocess_type']==1:
    json_res['preprocessing']="stemming"
  elif config_params['preprocess_type']==2:
    json_res['preprocessing']="lemmatization"
  elif config_params['preprocess_type']==3:
    json_res['preprocessing']="none"

  json_res['spell_check']=config_params['spell_check']

  if config_params['tf_scheme']==1:
    json_res['tf_scheme']="Normal TF"
  elif config_params['tf_scheme']==2:
    json_res['tf_scheme']="1+log(tf)"
  elif config_params['tf_scheme']==3:
    json_res['tf_scheme']="log(1+tf)"


  if len(docs)<config_params['result_size']:
    json_res['number_of_hits']=len(docs)
  else:
    json_res['number_of_hits']=config_params['result_size']

  if(len(docs)>config_params['result_size']):
    docs=docs[:config_params['result_size']]
    if config_params['index']==1:
      scores=scores[:config_params['result_size']]

  json_res['hits']=[]
  for j in range(len(docs)):
    resdict={"_source":{}}
    resdict["_source"]['id']=docs[j]
    resdict["_source"]['document_name']=data_dict['rowdict'][docs[j]][1]
    resdict["_source"]['Station']=data_dict['rowdict'][docs[j]][2]
    resdict["_source"]['Show']=data_dict['rowdict'][docs[j]][3]
    resdict["_source"]['Snippet']=data_dict['rowsnip'][docs[j]]
    if config_params['index']==1:
      resdict['score']=scores[j]
    json_res['hits'].append(resdict)
  return json_res


if __name__ == "__main__":
  #query = "NOT(brazil's government was defending its plan to build dozens of huge)"
  query = "brazil's government was defending OR potent than carbon dioxide that undermines the greenhouse gas advantage. reporter: bottom line"
  #query = "<BBCNEWS.201701> brazil's government is defending its plan to build dozens of huge"
  #query = input()
  #query="scientific community"

  print("The query is", query)
  doclist, time = main(query)
  print(json.dumps(doclist,indent=1))
  if config_params["index"] == 1:
    if "prev_queries.csv" in os.listdir("data"):
      df = pd.read_csv(os.path.join("data", "prev_queries.csv"), index_col=False)
    else:
      df = pd.DataFrame(columns = ["Query", "Time", "station", "show", "document", "rowid", "row_snippet"])
    df = df.append({
      "Query":query,
      "Time":datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
      "station": doclist['hits'][0]["_source"]["Station"],
      "show":doclist['hits'][0]["_source"]['Show'],
      "document": doclist['hits'][0]["_source"]["document_name"],
      "rowid" : doclist['hits'][0]["_source"]['Snippet'],
      "row_snippet" : doclist['hits'][0]["_source"]['id']}, ignore_index = True)
    df.to_csv(os.path.join("data", "prev_queries.csv"), index = None)
