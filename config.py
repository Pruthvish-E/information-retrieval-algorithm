config_params={
  'preprocess_type': 1,
  "stopword_removal" : 1,
  "index" : 1,
  "tf_scheme" : 1,
  "threshold_score" : 0,
  "spell_check" : False,
  "es_index" : "perf_test",
  "result_size" : 20,
  "es_preprocess" : False,
  "es_host" : "localhost",
  "es_port" : 9200
}
#preprocess_type : 1 is for stemming, 2 is for lemmatization , 3 is for none
#stop-word removal : 1 is to do stop-word removal , 0 is to not do stop word removal
#index : 1 is for tf-idf, 2 is for boolean query, 3 for Positional Index
#tf scheme : 1 is directly taking tf, 2 is 1+log(tf), 3 is log(1+tf)
#threshold_score : The minimum normalized threshold score for a document. 
#uses top 10 percentile if no document crosses this threshold
#spell_check: A flag to toggle spelling correction using edit distance.
#es_index : name for the elasticsearch index.
#result_size : the maximum number of documents a search shoukld return.
#es_preprocess : A flag to toggle preprocessing for elastic search.
#es_host and es_port : The hostname and port number for the elasticsearch server.
