import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import json
import random

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Load the trained model and data
model = load_model('model.h5')
words = pickle.load(open('texts.pkl', 'rb'))
classes = pickle.load(open('labels.pkl', 'rb'))
intents = json.load(open('data.json', 'r'))

# Download required NLTK data (if not already downloaded)
nltk.download('punkt')
nltk.download('wordnet')

# Function to clean up and tokenize user input
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Function to create a bag of words
def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return np.array(bag)

# Function to predict the class (intent) of the input
def predict_class(sentence, model, threshold=0.25):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    results = [[i, r] for i, r in enumerate(res) if r > threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

# Function to get a response based on the predicted intent
def get_response(intents_list, intents_json):
    if not intents_list:
        return "Sorry, I didn't understand that. Could you please rephrase?"
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    return "Sorry, I didn't understand that. Could you please rephrase?"

# Main chatbot function
def chatbot_response(text):
    intents_pred = predict_class(text, model)
    res = get_response(intents_pred, intents)
    return res

# Interactive chat loop
print("Medical Chatbot is running! Type 'quit' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        print("Chatbot: Goodbye!")
        break
    response = chatbot_response(user_input)
    print(f"Chatbot: {response}")