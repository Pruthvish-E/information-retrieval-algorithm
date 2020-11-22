import os
import sys
import re
import random
import pickle

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from preprocess import preprocess_sentence
from config import config_params
from utils.timer import timer_decorator
import metrics
import pandas as pd

def compare_scores(snippets):
    corpus = ''.join(snippets)
    corpus_list = corpus.split('.')
    scores_dict = dict()
    F1avg = 0
    valid_F1 = 0
    happ_avg_time = 0
    es_avg_time = 0
    for query in snippets:
        count=0
        print("iteration number:", valid_F1)
        print(query)

        # preprocess the query
        if config_params["es_preprocess"] :
            query = " ".join(preprocess_sentence(query)) 
        if(len(query.split()) < 4):
            count+=1
            continue
        scores = metrics.metrics(query)

        precision = scores[0] / (scores[0] + scores[1] + 1e-9)
        recall = scores[0] / (scores[0] + scores[2] + 1e-9)
        F1 = 2*precision*recall/(precision + recall + 1e-9)
        scores_dict[query] = [F1, precision, recall, scores[4], scores[5]]
        valid_F1 += 1
        happ_avg_time += scores[4]
        es_avg_time += scores[5]
        F1avg += F1
        print('scores:', scores)
        print('F1-score:', F1, 'precision:', precision, 'recall:', recall)
        print()
    print(F1avg/(valid_F1), happ_avg_time/valid_F1, es_avg_time/valid_F1)
    return scores_dict

def compare(snippets):
    try:
        print('in try block')
        f = open('data/scores.pkl', 'rb')
        scores_dict = pickle.load(f)
        f.close()
        scores_dict.update(compare_scores(snippets))
    except:
        print('in except')
        scores_dict = compare_scores(snippets)
    finally:
        print('in finally')
        print(scores_dict)
        f = open('data/scores.pkl', 'wb')
        pickle.dump(scores_dict, f)
        f.close()

if __name__ == "__main__":
    #f = open('data/data.pkl', 'rb')
    #snippets = list(pickle.load(f)['rowsnip'].values())
    #f.close()
    df = pd.read_csv("out.csv")
    snippets = df["query"]
    compare(snippets)
