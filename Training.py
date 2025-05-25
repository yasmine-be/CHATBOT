import random
import numpy as np
import json
import pickle
import  nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
nltk.download('punkt_tab')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
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
words = sorted(list(set(words)))  
print(words)
# Sauvegarder words et classes pour une réutilisation
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Créer les données d'entraînement (bag of words)
training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    word_patterns = doc[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

output_row = list(output_empty)
output_row[classes.index(doc[1])] = 1
training.append([bag, output_row])

random.shuffle(training)
training = np.array(training, dtype=object)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

print("Mots après lemmatisation :", words)
print("Classes :", classes)
print("Exemple de documents :", documents[:5])  # Afficher quelques documents pour vérification

# Étape 3 : Construire le réseau neuronal
def build_neural_network(num_words, num_classes):
    model = Sequential()
    model.add(Dense(128, input_shape=(num_words,), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))

    sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    
    return model

# Étape 4 : Entraîner le réseau neuronal
def train_neural_network(model, train_x, train_y):
    history = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1, validation_split=0.2)
    model.save('chatbot_model.h5')
    
    # Afficher la précision finale
    final_accuracy = history.history['accuracy'][-1]
    final_val_accuracy = history.history['val_accuracy'][-1]
    print(f"Précision finale sur les données d'entraînement : {final_accuracy:.4f}")
    print(f"Précision finale sur les données de validation : {final_val_accuracy:.4f}")
    
    return model
# Étape 5 : Construire le chatbot
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, word in enumerate(words):
            if word == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence, model, words, classes):
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    if not intents_list:
        return "Désolé, je ne comprends pas. Pouvez-vous décrire vos symptômes plus précisément ?"
    tag = intents_list[0]['intent']
    for intent in intents_json['intents']:
        intent_tag = intent['tag'] if isinstance(intent['tag'], str) else intent['tag'][0]
        if intent_tag == tag:
            return random.choice(intent['responses'])
    return "Désolé, je ne comprends pas."