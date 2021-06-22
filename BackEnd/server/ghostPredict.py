import json, sys
import os, re, io, glob
from google.cloud import vision
from google.cloud import storage
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from expertai.nlapi.cloud.client import ExpertAiClient
import keras
import tensorflow as tf
from keras.models import Sequential, model_from_json
from keras.layers import Dense
from tensorflow.python.keras.optimizers import TFOptimizer
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

def getFeatures(totalText, numMessages):
    # Set Expert AI Ennv variables
    os.environ['EAI_USERNAME'] = ''
    os.environ['EAI_PASSWORD'] = ''

    TaxonomyFeatures = ["Anger", "Irritation", "Exasperation", "Anxiety","Fear","Stress","Worry","Disgust","Repulsion","Guilt","Shame","Embarrassment","Regret","Boredom", "Hatred", "Offence", "Jealousy", "Envy","Sadness","Torment","Suffering","Disappointment","Disillusion", "Resignation", "Surprise","Happiness","Excitement","Joy","Amusement","Well-Being","Satisfaction","Relief","Like","Trust","Affection","Love","Passion","Empathy","Compassion","Asociality","Impoliteness","Ungratefulness","Emotionality","Isolation","Disagreement","Seriousness","Introversion","Unreservedness","Humour","Sexuality","Extroversion","Pleasantness","Trustfulness","Gratefulness","Empathy","Sedentariness","Passivity","Calmness","Initiative","Dynamism","Rejection","Apathy","Apprehension","Traditionalism","Conformism","Negativity","Bias","Cautiousness","Progressiveness","Acceptance","Courage","Positivity","Curiosity","Superficiality","Unawareness","Disorganization","Insecurity","Ignorance","Illusion","Awareness","Spirituality","Concern","Knowledge","Self-confidence","Organization","Violence","Extremism","Discrimination","Dishonesty","Neglect","Unlawfulness","Irresponsibility","Honesty","Compassion","Commitment","Lawfulness","Solidarity","Inclusiveness","Lack of intelligence","Inexperience","Incompetence","Rationality","Smartness","Creativity","Competence","Dissoluteness","Gluttony","Materialism","Addiction","Healthy lifestyle","Self-restraint"]
    
    print("Processing Features")
    x = np.zeros((len(TaxonomyFeatures)+3))
    aiClient = ExpertAiClient()
    
    aiClient = ExpertAiClient()
    output = aiClient.specific_resource_analysis(
                body={"document": {"text": totalText}}, 
                params={'language': "en", 'resource': 'sentiment'
    })
    sentiment = output.sentiment.overall
    output = aiClient.classification(body={"document": {"text": totalText}}, params={'taxonomy': "behavioral-traits", 'language': "en"})
    for category in output.categories:
        x[TaxonomyFeatures.index(category.hierarchy[len(category.hierarchy)-1])]=1
    output = aiClient.classification(body={"document": {"text": totalText}}, params={'taxonomy': "emotional-traits", 'language': "en"})
    for category in output.categories:
        x[TaxonomyFeatures.index(category.hierarchy[len(category.hierarchy)-1])]=1
    x[len(TaxonomyFeatures)] = sentiment
    x[len(TaxonomyFeatures)+1] = numMessages
    x[len(TaxonomyFeatures)+2] = len(totalText)/numMessages
    return x

def loadModel():
    import h5py
    gcs_source_uri = "gs://chadvice.appspot.com/models/ghostModel.h5"
    
    storage_client = storage.Client()
    
    match = re.match(r'gs://([^/]+)/(.+)', gcs_source_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)
    prefix2 = "models/ghostModel.json"
    print("bucket_name : ",bucket_name)
    print("prefix : ",prefix)
    bucket = storage_client.get_bucket(bucket_name)
    # List objects with the given prefix.
    blob_list1 = list(bucket.list_blobs(prefix=prefix))
    blob_list2 = list(bucket.list_blobs(prefix=prefix2))
    print('Output files:')
    
    blob = blob_list1[0]
    blob2 = blob_list2[0]
    print(blob.name)
    print(blob2.name) 
    blob.download_to_filename(os.getcwd()+"/ghostModel.h5")
    blob2.download_to_filename(os.getcwd()+"/ghostModel.json")
    loaded_model = loadModelLocal()
    print("Loaded model from Cloud Storage")
    os.remove(os.getcwd()+"/ghostModel.h5")
    os.remove(os.getcwd()+"/ghostModel.json")
    return loaded_model

def loadModelLocal():
    # load json and create model
    json_file = open('ghostModel.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("ghostModel.h5")
    print("Loaded model from disk")
    loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return loaded_model

def predict(totalText, numMessages):
    x = np.asarray(getFeatures(totalText, numMessages))
    loaded_model = loadModel()
    x = x.reshape(1, 114)
    return round(loaded_model.predict_proba(x)[0][0]*4)
    