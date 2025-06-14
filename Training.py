import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import random



nltk.download('punkt')
nltk.download('wordnet')

words = []
classes = []
documents = []
ignore_words = ['?', '!']
data_file = open('data.json').read()
intents = json.loads(data_file)


for intent in intents['intents']:
    for pattern in intent['patterns']:
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w, intent['tag']))
        # Check if tag is a list, and take the first element if needed
        tag = intent['tag']
        if isinstance(tag, list):
            tag = tag[0]  # Use the first tag if it's a list
        if tag not in classes:
            classes.append(tag)

# Process words and classes
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(set(words))
classes = sorted(set(classes))
print(len(documents), "documents")
print(len(classes), "classes", classes)
print(len(words), "unique lemmatized words", words)

# Save words and classes
pickle.dump(words, open('texts.pkl', 'wb'))
pickle.dump(classes, open('labels.pkl', 'wb'))

# Prepare training data
train_x = []
train_y = []
output_empty = [0] * len(classes)
for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # Create bag with consistent length
    for w in words:
        if w in pattern_words:
            bag.append(1)
        else:
            bag.append(0)
    
    # Use the first tag if doc[1] is a list
    tag = doc[1] if isinstance(doc[1], str) else doc[1][0]
    output_row = list(output_empty)
    output_row[classes.index(tag)] = 1
    
    train_x.append(bag)  # Append bag to train_x (features)
    train_y.append(output_row)  # Append output_row to train_y (labels)

# Shuffle both train_x and train_y together
combined = list(zip(train_x, train_y))
random.shuffle(combined)
train_x, train_y = zip(*combined)

# Convert to NumPy arrays
train_x = np.array(train_x)
train_y = np.array(train_y)
print("Training data created")

# Define and train the model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Fix SGD optimizer parameters
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)  # Removed 'decay'
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
model.save('model.h5', hist)

print("model created")