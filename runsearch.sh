#!/bin/bash
# Command to run this file:
# runsearch.sh "query" [preprocess]


if [ $# -ge 2 ]
then
  python preprocess.py
fi

if [ $# -ge 1 ]
then
  python metrics.py "$1"
else
  echo "Please enter the query string as the first parameter"
fi 
