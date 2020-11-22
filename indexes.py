from collections import defaultdict, Counter
from math import log10, sqrt
from preprocess import preprocess_sentence
from config import config_params
from functools import reduce
from nltk.corpus import words
from nltk.metrics import edit_distance
import pickle
import copy
from utils import bstree
from utils.bstree import BSTNode
from utils import colorize

with open("data/data.pkl", "rb") as f:
  data_dict = pickle.load(f)

class Index:
  """
  A base class for different indexes.
  The constructor expects a corpus dictionary with doc_id : [terms list] mapping
  Query function returns a list of matching doc id's.

  """
  def process_spell_errors(self, query):
    """
    Process the query string and replace spell errors with words from the
    corpus / english dictionary.

    query: A query string.

    """
    if config_params['spell_check']:
      split_query = query.split()
      result = []
      words_list = set(words.words()).union(data_dict['word_corpus'])

      for word in split_query:
        if word not in words_list and '*' not in word:
          print(colorize.magenta("%s is not in dict"%word))
          #process
          words_distance = zip(words_list, map(lambda x : edit_distance(word, x), words_list))
          best_word = reduce(lambda x,y : x if x[1]<=y[1] else y, words_distance)[0]
          word = best_word
          print(colorize.green("replaced with %s"%word))
        result.append(word)
      query = result
      return " ".join(query)
    return query

  def query(self, q):
    pass

  def __init__(self, corpus_dictionary):
    pass

class TFIDFIndex(Index):
  index = defaultdict(lambda : defaultdict(int)) #index[term][docid] = tf(doc, term)
  idf = defaultdict(set)    #idf[term] = idf(term)
  ndocs = 0

  def __init__(self, corpus_dictionary):
    """__init__.
     The constructor for TFIDF index
    :param corpus_dictionary: A dictionary with doc_id : [term_list] mapping
    """

    self.ndocs = len(corpus_dictionary)

    #build the inverted index
    for doc in corpus_dictionary:
      for term in corpus_dictionary[doc]:
        self.index[term][doc] += 1
        self.idf[term].add(doc)

    for term in self.idf:
      self.idf[term] = log10(self.ndocs/len(self.idf[term]) + 1e-10)

  def tfidf_score(self, tf, idf):
    """tfidf_score. - Returns the TFIDF partial score based on the scheme.
    :param tf: Term Frequency
    :param idf: Inverse document frequency
    """
    if config_params['tf_scheme'] == 1:
      tf_idf=tf*idf
    if config_params['tf_scheme'] == 2:
      tf_idf=1+log10(tf+1e-10)
    if config_params['tf_scheme'] == 3:
      tf_idf=log10(1+tf)*idf
    return tf_idf

  def query(self, query_string):
    """query the tfidf index  and return the list of matching doc IDs.

    :param query_string: A query string
    """
    #returns a sorted list of docids, with decreasing cosine similarity
    query_string = self.process_spell_errors(query_string)

    query_terms = preprocess_sentence(query_string)
    query_frequencies = Counter(query_terms) #query_term : frequency(query_term) in the query

    dotproducts = defaultdict(int) #sum of dotproduct elements of tfidf of the query and the document
    magnitude = defaultdict(int) #stores the magnitude of the document tfidf vector
    query_magnitude = 0

    #calculate the cosine similarity for the docs
    for term in query_frequencies.keys():

      if term not in self.index:
        continue

      query_tfidf = self.tfidf_score(query_frequencies[term], self.idf[term])
      query_magnitude += query_tfidf**2
      for doc in self.index[term]:
        doc_tfidf = self.tfidf_score(self.index[term][doc], self.idf[term])
        dotproducts[doc] += query_tfidf * doc_tfidf
        magnitude[doc] += doc_tfidf**2

    query_magnitude = sqrt(query_magnitude)
    cosine_similarity = {}
    for doc in magnitude:
        cosine_similarity[doc] = dotproducts[doc] / (query_magnitude * sqrt(magnitude[doc]) + 1e-10)

    ranked_docs = list(cosine_similarity.items())
    ranked_docs = sorted(ranked_docs, key = lambda x : x[1], reverse = True)
    threshold_docs = list(filter(lambda x : x[1]>config_params["threshold_score"], ranked_docs))
    #return docs with score>threshold, or the top 10% docs
    return threshold_docs if len(threshold_docs) else ranked_docs[:len(ranked_docs)//10 + 1]

class BooleanQuery(Index):
  """
  BooleanQuery Index.

  """

  index = defaultdict(set) #index[term][docid] = tf(doc, term)
  ndocs = 0
  term_set=set()
  reversed_set=set()
  reverse_terms=[]
  term_list=[]

  def __init__(self, corpus_dictionary):
    """__init__.
    Constructor for the BooleanQuery Index.
    :param corpus_dictionary:  A dictionary with doc_id to [token_list] mapping
    """

    self.ndocs = len(corpus_dictionary)

    for doc in corpus_dictionary:
      for term in corpus_dictionary[doc]:
        self.reversed_set.add(term[::-1])
        self.term_set.add(term)
        self.index[term].add(doc)

    self.term_list=sorted(list(self.term_set))[2:]
    self.reverse_terms=sorted(list(self.reversed_set))[2:]
    self.tree=BSTNode(self.term_list)#bst of terms
    self.reverse_tree=BSTNode(self.reverse_terms)#bst of terms reversed

  def query_or(self, query_terms):
    """query_or.
    A function that returns the union of all the doc_ids in the query terms.

    :param query_terms: A list of query terms.
    """
    query_terms.sort(key=lambda x: len(self.index[x]))
    res= list(reduce(lambda x,y:x.union(y),map(lambda x:self.index[x], query_terms)))
    return res

  def get_words_from_tree(self, tree, term):
    """get_words_from_tree.
    A helper function to retrieve a list of words from parameter "tree"
    Using the string "term".

    :param tree: A BSTNode representing the tree.
    :param term: A string representing a wildcard query term.
    """
    temp_terms = []
    node=tree.search(term)
    while node and node.val < term[:-1]+chr(ord(term[-1])+1):
      temp_terms.append(node.val)
      node=tree.inOrderSuccessor(node)
    return temp_terms

  def update_doclist(self, result_docs, terms):
    """update_doclist.
    A helper function to update an existing result_docs set or create one using the docs of "terms"

    :param result_docs: A set of doc_ids
    :param terms: Query term.
    """
    ans = set(result_docs)
    if len(result_docs)==0:
      ans.update(self.query_or(terms))
    else:
      ans=result_docs.intersection(self.query_or(terms))
    return ans

  def query(self, query_string):
    """query.
    A function that returns a set of doc IDs that match the given query string.
    Works on 1 level of nesting. 
    #TODO: Create an expression tree to handle arbitrary nesting.

    :param query_string: A query string.
    """
    all_list=[i for i in range(94858)]
    all_list=set(all_list)
    if query_string[3]=='(' and query_string[-1]==')':
      return list(all_list.difference(self.query(query_string[4:-1])))
    good_queries=[]
    if 'OR' in query_string:
      queries=query_string.split('OR')
    else:
      queries=[query_string]

    results=[]
    for query in queries:

      if 'NOT' in query:
        if query[0]!='N': 
          query_=query.split('NOT')
          not_queries=set(self.break_query(query_[1][1:-1]))
          good_queries_=set(self.break_query(query_[0]))
          good_queries_=list(good_queries_.intersection(all_list.difference(not_queries)))
          good_queries.extend(good_queries_)
        else:
          brack_ind=query.index(')')
          not_queries=set(self.break_query(query[4:brack_ind]))
          good_queries_=set(self.break_query(query[brack_ind+1:]))
          good_queries_=list(good_queries_.intersection(all_list.difference(not_queries)))
          good_queries.extend(good_queries_)
      else:
        good_queries.extend(self.break_query(query))
    good_queries=set(good_queries)
    return list(good_queries)

  def break_query(self, query_string):
    """break_query.
    A function to split a query based on wildcard operators

    :param query_string: A query string
    """
    star_flag=0
    query_string = self.process_spell_errors(query_string)
    query_terms = preprocess_sentence(query_string)
    result_docs = set()
    new_query_terms=[]

    for term in query_terms:
      if '*' in term:
        #prefix query
        star_flag=1
        if term[-1]=='*':
          term=term[:-1]
          temp_terms = self.get_words_from_tree(self.tree, term)
          result_docs = self.update_doclist(result_docs, temp_terms)

        elif term[0]=='*':
          #suffix query
          term=term[1:][::-1]
          temp_terms = []
          temp_terms = self.get_words_from_tree(self.reverse_tree, term)
          result_docs = self.update_doclist(result_docs, temp_terms)
        else:
          #prefix+suffix query
          pref_terms = []
          suff_terms = []
          star_index=term.index('*')
          prefix_term=term[:star_index]
          suffix_term=term[star_index+1:]

          pref_terms = self.get_words_from_tree(self.tree, prefix_term)
          suffix_term = suffix_term[::-1]
          suff_terms = [i[::-1] for i in self.get_words_from_tree(self.reverse_tree, suffix_term)]
          result_docs = self.update_doclist(result_docs, list(set(pref_terms).intersection(set(suff_terms))))

      else:
          new_query_terms.append(term)

    query_terms=new_query_terms
    query_terms.sort(key=lambda x: len(self.index[x]))

    #if it is a wild card query
    if star_flag==1:
      if(len(query_terms)!=0):
        result_docs=set(reduce(lambda x,y:x.intersection(y),map(lambda x:self.index[x], query_terms))).intersection(result_docs)
      return list(result_docs)


    if(len(query_terms)==0):
      return list()
    return list(set(reduce(lambda x,y:x.intersection(y),map(lambda x:self.index[x], query_terms))))

class PositionalIndex(Index):
  """PositionalIndex.
  A positional Index implementation for queries

  """

  def __init__(self, corpus_dictionary):
    self.ndocs = len(corpus_dictionary)
    self.index = defaultdict(lambda : defaultdict(set))
    for doc in corpus_dictionary:
        position=0
        for term in corpus_dictionary[doc]:
          self.index[term][doc].add(position)
          position+=1

  def query(self,query_string):
    query_string = self.process_spell_errors(query_string)
    query_terms = preprocess_sentence(query_string)
    query_docs = []
    for i in range(len(query_terms)):
      newdocdict = copy.deepcopy(self.index[query_terms[i]])
      for doc in newdocdict:
        #doc is an id with value = list
        newdocdict[doc] = set(map(lambda x: x-i, newdocdict[doc]))
      query_docs.append(newdocdict)

    #query docs is a list of dictionaries, where each dict correpsonds to the posting list of 1 query term
    answer = []
    for doc in query_docs[0]:
      #do something
      docflag = True
      for position in query_docs[0][doc]:
        posflag = True
        for other_doclist in query_docs[1:]:
          if doc not in other_doclist:
            docflag = False
            break
          if position not in other_doclist[doc]:
            posflag = False
            break

        if docflag and posflag:
          answer.append(doc)
          break
        if not docflag:
          break
    return answer
