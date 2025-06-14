from flask import Flask, render_template, request, jsonify
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import json
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

lemmatizer = WordNetLemmatizer()


try:
    print("Loading model and data files...")
    model = load_model('model.h5')
    words = pickle.load(open('texts.pkl', 'rb'))
    classes = pickle.load(open('labels.pkl', 'rb'))
    intents = json.load(open('data.json', 'r', encoding='utf-8'))
    
    
    print("\nModel loaded successfully!")
    print("Model summary:")
    model.summary()
    print("\nLoaded words:", len(words))
    print("Sample words:", words[:5])
    print("\nLoaded classes:", classes)
    print("\nIntents sample:")
    for intent in intents['intents'][:2]:
        print(f"Tag: {intent['tag']}")
        print(f"Patterns: {intent['patterns'][:2]}...")
        print(f"Responses: {intent['responses'][:2]}...")
        print()
        
except Exception as e:
    print("\nERROR LOADING FILES:", str(e))
    raise e

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return np.array(bag)

def predict_class(sentence, model, threshold=0.01):  # Lowered threshold
    p = bow(sentence, words)
    res = model.predict(np.array([p]))[0]
    
    # Debug prints
    print("\nInput sentence:", sentence)
    print("Bag of words shape:", p.shape)
    print("Raw predictions:", res)
    
    results = [[i, r] for i, r in enumerate(res) if r > threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": float(r[1])})
    
    print("Predicted intents:", return_list)
    return return_list

def get_response(intents_list, intents_json):
    if not intents_list:
        print("No intent matched - using default response")
        return "Désolé, je n'ai pas compris. Pouvez-vous reformuler votre question médicale ?"
    
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    
    for i in list_of_intents:
        if i['tag'] == tag:
            response = random.choice(i['responses'])
            print(f"Matched intent '{tag}' with response: {response}")
            return response
    
    print("Intent matched but no response found - using default")
    return "Désolé, je n'ai pas trouvé de réponse appropriée à votre question médicale."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({'response': "Veuillez entrer un message valide."})
        
        print("\n" + "="*50)
        print(f"Received message: '{user_message}'")
        
        intents_pred = predict_class(user_message, model)
        response = get_response(intents_pred, intents)
        
        disclaimer = "\n\n❤️ Your Well-Being Comes First"
        return jsonify({'response': response + disclaimer})
        
    except Exception as e:
        print("Error processing message:", str(e))
        return jsonify({'response': "Une erreur s'est produite. Veuillez réessayer."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)