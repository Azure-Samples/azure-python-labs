
import json
import numpy
import numpy as np
import pandas as pd
import os
import pickle
from sklearn.externals import joblib
from azureml.core.model import Model
from reco_utils.dataset import movielens
from reco_utils.dataset.python_splitters import python_random_split
from reco_utils.evaluation.python_evaluation import map_at_k, ndcg_at_k, precision_at_k, recall_at_k
from reco_utils.recommender.sar.sar_singlenode import SARSingleNode

# load the model
def init():
    global model
    # retrieve the path to the model file using the model name
    model_path = Model.get_model_path(model_name='movielens_sar_model')
    model = joblib.load(model_path)

# Passes data to the model and returns the prediction
def run(raw_data):
    # make prediction
    try: 
        data = raw_data
        data = pd.read_json(data)
        return model.get_item_based_topk(items=data, sort_top_k=True).to_json()
    except Exception as e:
        error = str(e)
        return error
