#imports
import time
import numpy
import pickle
import os

import unicodedata
import re
import numpy as np
import pandas as pd
import sys
import nltk
import multiprocessing

from tqdm import tqdm
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords
from config import config_params

#preprocessing
def unicode_to_ascii(s):
  return ''.join(c for c in unicodedata.normalize('NFD', s)
      if unicodedata.category(c) != 'Mn')


#initialize the stemmer and lemmatizer
lemmatizer = WordNetLemmatizer()
ps = PorterStemmer()
stopword_set = set(stopwords.words('english'))


def preprocess_sentence(w):
  """
  This function takes in the sentence and returns a list of words which are applied to various methods of preprocessing
  Inputs:
    w : The input sentence
  Outputs:
    preprocessed_sent : The preprocessed list of terms of the sentence.
  """
  w = unicode_to_ascii(w.lower().strip())

  # creating a space between a word and the punctuation following it
  w = re.sub(r"([?.!,¿])", r" \1 ", w)
  w = re.sub(r'[" "]+', " ", w)
  w=w.replace('.','')
  w=w.replace(',','')
  w=w.replace('!','')

  # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
  w = re.sub(r"[^a-zA-Z?.!,¿*1-9]+", " ", w)
  preprocessed_sent  = []
  w = w.strip()
  if "*" not in w:
    tokenized_list = nltk.word_tokenize(w)
    for i in tokenized_list:
      if config_params['preprocess_type']==1 and config_params['index']==1:
          i=ps.stem(i)
      elif config_params['preprocess_type']==2 and config_params['index']==1:
        i=lemmatizer.lemmatize(i)
      if config_params["stopword_removal"]==1 and i in  stopword_set:
        continue
      preprocessed_sent.append(i)
  else:
    tokenized_list = w.split()
    for i in tokenized_list:
      i=i.strip()
      if '*' in i:
        preprocessed_sent.append(i)
        continue
      elif config_params['preprocess_type']==1 and config_params['index']==1:
        i=ps.stem(i)
      elif config_params['preprocess_type']==2 and config_params['index']==1:
        i=lemmatizer.lemmatize(i)
      if config_params["stopword_removal"]==1 and i in  stopword_set:
        continue
      preprocessed_sent.append(i)


    #root form reductions based on condition
  return preprocessed_sent


def get_snippets():
  """
  This function generates the mappings of all snippets of the corpus, its terms and custom generated idss for the snippets and dumps them in a pickle file
  """
  #read the data
  #mapping from uuid to row, doc pair
  rowdict = {}
  #a dictionary that maps docid to its snippet
  rowsnip = {}
  #a dictionary that maps a row to its term list
  rowterms = {}
  word_corpus = set()

  docid = 0
  for i in sorted(os.listdir('TelevisionNews')):
    try:
      df =  pd.read_csv(os.path.join('TelevisionNews', i))
    except:
      print(i+" was not processed")
      continue

    for index, row in df.iterrows():
      rowdict[docid] = (index,  i, str(row['Station']).lower(), str(row["Show"]).lower())
      rowsnip[docid] = row["Snippet"]
      word_corpus.update(row["Snippet"].split())
      docid += 1


  pool = multiprocessing.Pool(multiprocessing.cpu_count())

  for doc in tqdm(rowsnip):
    rowterms[doc] = pool.apply_async(preprocess_sentence, (rowsnip[doc],))
  rt  = rowterms
  rowterms = {}
  for i in tqdm(rt):
    rowterms[i] = rt[i].get()
  #write the preprocessed document pickle files.
  with open(os.path.join('data', "data.pkl"), "wb") as f:
    pickle.dump({"rowsnip" : rowsnip, "rowterms":rowterms, "rowdict" : rowdict, "word_corpus" : word_corpus}, f)

if __name__ == "__main__":
  get_snippets()
