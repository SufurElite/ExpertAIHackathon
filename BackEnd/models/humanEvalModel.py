
#Importing libraries
import numpy as np 
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn.linear_model import LogisticRegression
from keras.preprocessing.sequence import pad_sequences

from keras.models import Sequential
from keras import layers
from keras.layers import Dense, Embedding, LSTM
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
import re
import json
import pandas as pd
import pickle 

maxlen = 400
embedding_dim = 100

def create_embedding_matrix(filepath, word_index, embedding_dim):
    """ If I have time to use glove word embeddings """
    vocab_size = len(word_index) + 1  # Adding again 1 because of reserved 0 index
    embedding_matrix = np.zeros((vocab_size, embedding_dim))

    with open(filepath) as f:
        for line in f:
            word, *vector = line.split()
            if word in word_index:
                idx = word_index[word] 
                embedding_matrix[idx] = np.array(
                    vector, dtype=np.float32)[:embedding_dim]

    return embedding_matrix

def get_data():
    df = pd.read_json("humanEvalData/inquisitive.json")
    data = df[['X', 'y']]    
    sentences = data["X"].values 
    y = to_categorical(data["y"].values)
    sentences_train, sentences_test, y_train, y_test = train_test_split(sentences, y, test_size=0.15, random_state=42)
    tokenizer = load_tokenizer()
    vocab_size = len(tokenizer.word_index) + 1
    X_train = tokenizer.texts_to_sequences(sentences_train)
    X_test = tokenizer.texts_to_sequences(sentences_test)
    sentences = tokenizer.texts_to_sequences(sentences)

    X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
    X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)
    sentences = pad_sequences(sentences,padding='post',maxlen=maxlen)
    return sentences, y, X_train, X_test, y_train, y_test, vocab_size

def build_model(vocab_size):
    model = Sequential()
    model.add(layers.Embedding(vocab_size, embedding_dim, input_length=maxlen))
    model.add(layers.Conv1D(128, 5, activation='relu'))
    model.add(layers.GlobalMaxPooling1D())
    model.add(layers.Dense(50, activation='relu'))
    model.add(layers.Dense(4, activation='sigmoid'))
    model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
    return model

def save_tokenizer():
    # Create and ave the Tokenizer
    df = pd.read_json("humanEvalData/inquisitive.json")
    vals = list(df["X"].values)
    with open("imageData/vocab.txt","r") as f:
        vocab = f.read().split("\n")
        del vocab[len(vocab)-1]
    vals+=vocab
    tokenizer = Tokenizer(num_words=5000)
    tokenizer.fit_on_texts(vals)
    vocab_size = len(tokenizer.word_index) + 1
    with open("tokenizer.pkl","wb") as f:
        pickle.dump(tokenizer,f)

def load_tokenizer():
    with open("tokenizer.pkl","rb") as f:        
        tokenizer = pickle.load(f)
    return tokenizer

def save_model(model):
    model_json = model.to_json()
    with open("model_files/inquisitiveModel.json", "w+") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("model_files/inquisitiveModel.h5")
    print("Saved model to disk")

def main():
    X_total, y, X_train, X_test, y_train, y_test, vocab_size = get_data()
    model = build_model(vocab_size)
    print("Vocab Size: " + str(vocab_size))
    model.fit(X_train, y_train,
                    epochs=10,
                    verbose=True,
                    validation_data=(X_test, y_test),
                    batch_size=10)
    loss, accuracy = model.evaluate(X_train, y_train, verbose=True)
    print("Training Accuracy: {:.4f}".format(accuracy))
    loss, accuracy = model.evaluate(X_test, y_test, verbose=True)
    print("Testing Accuracy:  {:.4f}".format(accuracy))
    #save_model(model)

if __name__=="__main__":
    main()