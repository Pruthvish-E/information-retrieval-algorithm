import pickle
import pandas as pd

def populate_list(index):
    mylist = list()
    for key in list(scores_dict.keys()):
        mylist.append(scores_dict[key][index])
    return mylist

f = open('data/scores.pkl', 'rb')
scores_dict = pickle.load(f)
f.close()

F1_score_list = populate_list(0)
precision_list = populate_list(1)
recall_list = populate_list(2)
happ_time_list = populate_list(3)
es_time_list = populate_list(4)
query_list = list(scores_dict.keys())

df = pd.DataFrame({'query': query_list, 'F1_score': F1_score_list, 'precision': precision_list, 'recall': recall_list, 'happ_time': happ_time_list, 'es_time': es_time_list})
df.to_csv('out_100.csv', index = False)


