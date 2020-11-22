# Information-Retrieval Project

A search engine written in python. Uses [this](https://www.kaggle.com/amritvirsinghx/environmental-news-nlp-dataset) kaggle dataset, but can be configured to work on any set of documents.


### Running the search engine
---

0. Install all the required dependencies.

    ```pip install -r requirements.txt```
1. Make the required changes to `config.py`. Please refer to the comments in that file for options.
2. Run `preprocess.py`. This will generate a pickle file in `data/data.pkl`, which will be sued by the subsequent files.
3. Run `query.py` with the required query.
    - Alternatively run `flaskapp.py`. This will start a server on port 5000.
    - HTTP requests can be sent to the flask app to obtain results.
    - Our UI can be accessed at `localhost:5000`.
4. Run `metrics.py` with the appropriate query to compare results with elasticsearch. This needs an elasticsearch server to be running at the port mentioned in `config.py`.

### Setting Up ElasticSearch
---


### File Structure
---

ElasticSearch

* ES.py : This file builds the index for elastic search and functions to implement search in elastic search.
  
* compare.py : 

static/styles

* mainpage.css : css for the html file

templates

* search.html : htm file for user interface

TelevisionNews : This folder is the dataset used for the search engine.

utils:

* bstree.py : This file has functions to implement BST for wild card queries
colorize.py : helper module to colorize the outputs 

* timer.py : helper module to time the execution times of various query and index construction functions.

config.py : A file that holds all the config details for the 2 search engines

flaskapp.py : A module that is used to create a flask server. It serves a static HTML page that can be used to query our search engine. It also has a route, /search, that can be used to query the search engines using HTTP requests.

indexes.py : This file constructs the index for the corpus

metrics.py : A module that is used to calculate the performance metrics for a given query.

preprocess.py :  This file preprocesses the data from the dataset and writes it to a binary that can be read and used by subsequent modules. 

query.py : This file takes in the user query and based on the index mentioned in the config.py file, queries the respective index and returns the results.
