import json, sys, pickle
import os, re, io, glob
from google.cloud import vision
from google.cloud import storage
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from expertai.nlapi.cloud.client import ExpertAiClient
import keras
import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential, model_from_json
from tensorflow.python.keras.optimizers import TFOptimizer
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

def get_features(totalText, tokenizer):
    maxlen = 400
    x = tokenizer.texts_to_sequences([totalText])
    x = pad_sequences(x, padding='post', maxlen=maxlen)
    return x

def loadModel():
    import h5py
    gcs_source_uri = "gs://chadvice.appspot.com/models/inquisitiveModel.h5"
    
    storage_client = storage.Client()
    
    match = re.match(r'gs://([^/]+)/(.+)', gcs_source_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)
    prefix2 = "models/inquisitiveModel.json"
    prefix3 = "models/tokenizer.pkl"
    print("bucket_name : ",bucket_name)
    print("prefix : ",prefix)
    bucket = storage_client.get_bucket(bucket_name)
    # List objects with the given prefix.
    blob_list1 = list(bucket.list_blobs(prefix=prefix))
    blob_list2 = list(bucket.list_blobs(prefix=prefix2))
    blob_list3 = list(bucket.list_blobs(prefix=prefix3))
    print('Output files:')
    
    blob = blob_list1[0]
    blob2 = blob_list2[0]
    blob3 = blob_list3[0]
    print(blob.name)
    print(blob2.name) 
    print(blob3.name) 
    blob.download_to_filename(os.getcwd()+"/inquisitiveModel.h5")
    blob2.download_to_filename(os.getcwd()+"/inquisitiveModel.json")
    blob3.download_to_filename(os.getcwd()+"/tokenizer.pkl")

    loaded_model = loadModelLocal()
    load_tokenizer = load_tokenizer(os.getcwd()+"/tokenizer.pkl")
    print("Loaded model from Cloud Storage")
    os.remove(os.getcwd()+"/inquisitiveModel.h5")
    os.remove(os.getcwd()+"/inquisitiveModel.json")
    os.remove(os.getcwd()+"/tokenizer.pkl")
    return loaded_model, tokenizer

def load_tokenizer(fpath):
    with open(fpath,"rb") as f:        
        tokenizer = pickle.load(f)
    return tokenizer

def loadModelLocal():
    # load json and create model
    json_file = open('inquisitiveModel.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("inquisitiveModel.h5")
    print("Loaded model from disk")
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return loaded_model

def loadOnlyLocal():
    # load json and create model
    json_file = open('model_files/inquisitiveModel.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model_files/inquisitiveModel.h5")
    print("Loaded model from disk")
    tokenizer = load_tokenizer("tokenizer.pkl")
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return loaded_model, tokenizer

def predict(totalText):
    loaded_model, tokenizer = loadOnlyLocal()
    x = np.asarray(get_features(totalText, tokenizer))
    pred = loaded_model.predict(x)
    return pred.argmax()