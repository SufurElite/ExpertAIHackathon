import keras
import tensorflow as tf
from keras.models import Sequential, model_from_json
from keras.layers import Dense
from tensorflow.python.keras.optimizers import TFOptimizer
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

def getData():
    X = np.load(position_file)
    y = np.load(target_file)
    #input(X.shape)
    return X, y

def getModel():
    model = Sequential()
    model.add(Dense(200, input_dim=1023, activation='relu'))
    model.add(Dense(120, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train(X, y):  
    model = getModel()
    X = [X]
    print("Started Training")
    model.fit(X, y, epochs=100, batch_size=32)
    _, accuracy = model.evaluate(X, y)
    print('Accuracy: %.2f' % (accuracy*100))
    model_json = model.to_json()
    with open("modfiles/mod.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("modfiles/mod.h5")
    print("Saved model to disk")

if __name__=="__main__":
    X, y = getData()
    train(X, y)