import random
import numpy as np
import json
import pickle
import  nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.layers import Dense, Activation, Dropout
import nltk
nltk.download('punkt_tab')

lemmatizer = WordNetLemmatizer
intents = json.loads(open('data.json').read())

words = []
classes = []
documents = []
ignore_letters = ['?', '.', '!', ',']


for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list= nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list,  intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
print(documents)

words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(list(set(words)))  # Convert set back to list before sorting
print(words)