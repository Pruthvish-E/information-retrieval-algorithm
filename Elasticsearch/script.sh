#!/bin/sh

# run ES
#./elasticsearch
# ../../elasticsearch-7.9.3/bin/elasticsearch

# make sure ES is up and running
curl -X GET 'http://localhost:9200'
echo '\n'
sleep 1

# insert data from csv
# ../../logstash-7.9.3/bin/logstash -f ./logstash-csv.conf

# list all documents in an index
curl -X GET 'http://localhost:9200/test/_search?pretty=true&q=*government is defending its plan to build dozens*&size=12'
echo '\n'
