
import argparse
import os
import numpy as np
import pandas as pd
import itertools
import logging
import time

from azureml.core import Run
from sklearn.externals import joblib

from reco_utils.dataset import movielens
from reco_utils.dataset.python_splitters import python_random_split
from reco_utils.evaluation.python_evaluation import map_at_k, ndcg_at_k, precision_at_k, recall_at_k
from reco_utils.recommender.sar.sar_singlenode import SARSingleNode

TARGET_DIR = 'movielens'
OUTPUT_FILE_NAME = 'outputs/movielens_sar_model.pkl'
MODEL_FILE_NAME = 'movielens_sar_model.pkl'

# get hold of the current run
run = Run.get_context()

# let user feed in 2 parameters, the location of the data files (from datastore), and the regularization rate of the logistic regression model
parser = argparse.ArgumentParser()
parser.add_argument('--data-folder', type=str, dest='data_folder', help='data folder mounting point')
parser.add_argument('--data-file', type=str, dest='data_file', help='data file name')
parser.add_argument('--top-k', type=int, dest='top_k', default=10, help='top k items to recommend')
parser.add_argument('--data-size', type=str, dest='data_size', default=10, help='Movielens data size: 100k, 1m, 10m, or 20m')
args = parser.parse_args()

run.log("top-k",args.top_k)
run.log("data-size", args.data_size)
data_pickle_path = os.path.join(args.data_folder, args.data_file)

data = pd.read_pickle(path=data_pickle_path)

train, test = python_random_split(data,0.75)

# instantiate the SAR algorithm and set the index
header = {
    "col_user": "UserId",
    "col_item": "MovieId",
    "col_rating": "Rating",
    "col_timestamp": "Timestamp",
}

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)-8s %(message)s')

model = SARSingleNode(
    remove_seen=True, similarity_type="jaccard", 
    time_decay_coefficient=30, time_now=None, timedecay_formula=True, **header
)

# train the SAR model
start_time = time.time()

model.fit(train)

train_time = time.time() - start_time
run.log(name="Training time", value=train_time)

start_time = time.time()

top_k = model.recommend_k_items(test)

test_time = time.time() - start_time
run.log(name="Prediction time", value=test_time)

# TODO: remove this call when the model returns same type as input
top_k['UserId'] = pd.to_numeric(top_k['UserId'])
top_k['MovieId'] = pd.to_numeric(top_k['MovieId'])

# evaluate
eval_map = map_at_k(test, top_k, col_user="UserId", col_item="MovieId", 
                    col_rating="Rating", col_prediction="prediction", 
                    relevancy_method="top_k", k=args.top_k)
eval_ndcg = ndcg_at_k(test, top_k, col_user="UserId", col_item="MovieId", 
                      col_rating="Rating", col_prediction="prediction", 
                      relevancy_method="top_k", k=args.top_k)
eval_precision = precision_at_k(test, top_k, col_user="UserId", col_item="MovieId", 
                                col_rating="Rating", col_prediction="prediction", 
                                relevancy_method="top_k", k=args.top_k)
eval_recall = recall_at_k(test, top_k, col_user="UserId", col_item="MovieId", 
                          col_rating="Rating", col_prediction="prediction", 
                          relevancy_method="top_k", k=args.top_k)

run.log("map", eval_map)
run.log("ndcg", eval_ndcg)
run.log("precision", eval_precision)
run.log("recall", eval_recall)
# run.log_table("topk", top_k.to_dict())

# automatic upload of everything in ./output folder doesn't work for very large model file
# model file has to be saved to a temp location, then uploaded by upload_file function
joblib.dump(value=model, filename=MODEL_FILE_NAME)

run.upload_file(OUTPUT_FILE_NAME, MODEL_FILE_NAME)
