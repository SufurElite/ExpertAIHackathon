
#Importing libraries
import numpy as np 
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
import re
import json
import pandas as pd

#Converting into pandas dataframe and filtering only text and ratings given by the users
df = pd.read_json("data/inquisitive.json")
data = df[['X', 'y']]

data['X'] = data['X'].apply(lambda x: x.lower())
data['X'] = data['X'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))

tokenizer = Tokenizer(num_words = 2500, split=' ')

tokenizer.fit_on_texts(data['X'].values)
#print(tokenizer.word_index)  # To see the dicstionary
X = tokenizer.texts_to_sequences(data['X'].values)
X = pad_sequences(X)

embed_dim = 128
lstm_out = 300
batch_size= 32

##Buidling the LSTM network

model = Sequential()
model.add(Embedding(2500, embed_dim,input_length = X.shape[1], dropout=0.1))
model.add(LSTM(300, dropout=0.1, recurrent_dropout=0.1))
model.add(Dense(4,activation='softmax'))
model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])

y = data['y'].values
from keras.utils import to_categorical
y_binary = to_categorical(y)
X_train, X_valid, Y_train, Y_valid = train_test_split(X,y_binary, test_size = 0.20, random_state = 42)
#Here we train the Network.
input(X_train[0])
model.fit(X_train, Y_train, batch_size =batch_size, epochs = 1,  verbose = 5)

# Measuring score and accuracy on validation set

score,acc = model.evaluate(X_valid, Y_valid, verbose = 2, batch_size = batch_size)
print("Logloss score: %.2f" % (score))
print("Validation set Accuracy: %.2f" % (acc))