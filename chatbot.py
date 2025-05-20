import json
import random
import string
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
from flask import Flask, request, jsonify
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

warnings.filterwarnings('ignore')

app = Flask(__name__)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Load the JSON data
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Preprocess the data
intents = data['intents']

# Create a list of patterns and corresponding tags
patterns = []
tags = []
responses = {}

for intent in intents:
    # Handle both single tag and list of tags
    if isinstance(intent['tag'], list):
        current_tags = intent['tag']
    else:
        current_tags = [intent['tag']]
    
    for pattern in intent['patterns']:
        # Tokenize and lemmatize each pattern
        tokens = word_tokenize(pattern.lower())
        tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stopwords.words('english') + list(string.punctuation)]
        processed_pattern = ' '.join(tokens)
        
        patterns.append(processed_pattern)
        tags.append(current_tags[0])  # Use the first tag for pattern classification
    
    # Store responses by tag
    for tag in current_tags:
        responses[tag] = intent['responses']

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(patterns)

def preprocess_input(text):
    # Tokenize and lemmatize the input text
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stopwords.words('english') + list(string.punctuation)]
    return ' '.join(tokens)

def get_response(user_input):
    # Preprocess user input
    processed_input = preprocess_input(user_input)
    
    # Vectorize the input
    input_vector = vectorizer.transform([processed_input])
    
    # Calculate similarity scores
    similarity_scores = cosine_similarity(input_vector, tfidf_matrix)
    
    # Get the most similar pattern
    max_score_idx = similarity_scores.argmax()
    max_score = similarity_scores[0, max_score_idx]
    
    # Threshold for matching (adjust as needed)
    if max_score > 0.2:
        matched_tag = tags[max_score_idx]
        return random.choice(responses[matched_tag])
    else:
        return "I'm sorry, I don't understand. Could you please rephrase or provide more details about your symptoms?"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = get_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)