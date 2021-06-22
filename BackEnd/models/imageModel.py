import keras,json
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
from sklearn.model_selection import train_test_split
import numpy as np

def getData():
    with open("imageData/data.json") as f:
        data = json.load(f)
    X_tmp = data["X"]
    y_tmp = data["y"]
    X = []
    y = []
    assert(len(X)==len(y))
    for i in range(len(X_tmp)):
        try:
            X.append(np.asarray(X_tmp[i]).astype('float32'))
            y.append(y_tmp[i])
        except Exception as e:
            pass
    X = np.asarray(X)
    y = np.asarray(y)
    print(len(X),len(y))
    assert(len(y)==len(X))
    print(X.shape)
    print(y.shape)
    return X, y

def getModel():
    model = Sequential()
    model.add(Dense(400, input_dim=114, activation='relu'))
    model.add(Dense(120, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train(X, y):  
    model = getModel()
    print("Started Training")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    model.fit(X_train, y_train, epochs=100, batch_size=32)
    _, accuracy = model.evaluate(X_test, y_test)
    print('Accuracy: %.2f' % (accuracy*100))
    model_json = model.to_json()
    with open("model_files/ghostModel.json", "w+") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("model_files/ghostModel.h5")
    print("Saved model to disk")

if __name__=="__main__":
    X, y = getData()
    train(X, y)