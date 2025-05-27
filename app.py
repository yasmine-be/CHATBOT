import json
import random
import nltk
import pymysql
import datetime
#nltk.download('popular')
import pickle
import numpy as np
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from keras.models import load_model
model = load_model('model.h5')  
intents = json.loads(open('data.json').read())
words = pickle.load(open('texts.pkl','rb'))
classes = pickle.load(open('labels.pkl','rb'))
import json
from flask import Flask, render_template, request
from collections import Counter

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


def count_mots(filename):
    word_counts = {}
    ignore_words = ['le', 'la', 'oui', 'si', 'je', 'suis', 'me','veux','un']

    with open(filename, 'r') as file:
        for line in file:
            words = line.split()
            for word in words:
                word = word.lower()
                if word not in ignore_words:
                    if word in word_counts:
                        word_counts[word] += 1
                    else:
                        word_counts[word] = 1

    return word_counts


def write_mots(word_counts, output_filename):
    sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    with open(output_filename, 'w') as file:
        for word, count in sorted_counts:
            file.write(f"{word}: {count}\n")



def AI():
    input1 = 'input.txt'
    output1 = 'output.txt'
    word_counts = count_mots(input1)
    write_mots(word_counts, output1)
    insert(output1)
    print("Terminé")


def ai(res, msg):
    if (res == "Je ne comprends pas. Pouvez-vous reformuler votre question, s'il vous plait?"):
        with open('input.txt', 'a+') as file:
            file.seek(0)  
            existing_content = file.read().strip()  
            file.seek(0, 2) 
            if existing_content:
                file.write('\n') 
            file.write(msg)  
        return AI()


import pymysql

def insert(filename):
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="restaurant"
    )
    try:
        with open(filename, 'r') as file:
            data = [line.strip().split(': ') for line in file]         
            with connection.cursor() as cursor:
                # Get all existing words from the database
                query_get_existing = "SELECT mot FROM ai"
                cursor.execute(query_get_existing)
                existing_words = set([row[0] for row in cursor.fetchall()])
                words_to_delete = existing_words - set([word for word, _ in data])
                if words_to_delete:
                    query_delete = "DELETE FROM ai WHERE mot IN %s"
                    cursor.execute(query_delete, (tuple(words_to_delete),))
                for word, count in data:
                    query_check = "SELECT COUNT(*) FROM ai WHERE mot = %s"
                    cursor.execute(query_check, (word,))
                    result = cursor.fetchone()
                    word_exists = result[0] > 0
                    if word_exists:
                        query_update = "UPDATE ai SET count = %s WHERE mot = %s"
                        cursor.execute(query_update, (count, word))
                    else:
                        query_insert = "INSERT INTO ai (mot, count) VALUES (%s, %s)"
                        cursor.execute(query_insert, (word, count))
        
        connection.commit()
        print("done")
    
    finally:
        connection.close()





def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    ai(res, msg)
    return res




       
    

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="restaurant"
)




app = Flask(__name__)
app.static_folder = 'static'

@app.route("/post", methods=['POST'])
def dhow():
     nom = request.args.get('nom')
     return nom

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=['GET'])
def get_bot_response():
     msg = request.args.get('msg')
     res = chatbot_response(msg)
     return res
 
def oldcli(nom, prenom, num, restaurant):
    connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="restaurant"
    )
    cursor = connection.cursor()
    query = "SELECT id FROM {} where nom=%s and prenom=%s and num=%s".format(restaurant)
    cursor.execute(query, (nom, prenom, num))
    num_rows = cursor.rowcount    
    cursor.close()
    return num_rows


def verifier_reservations(date, heure,restaurant):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="restaurant"
    )
     
    try:
        # Ouvrir une connexion à la base de données
        cursor = conn.cursor()
        
        # Convertir l'heure saisie en objet time
        heure_reservation = datetime.datetime.strptime(heure, "%H:%M").time()
        
        # Heure de début (heure - 1 heure)
        heure_deb = (datetime.datetime.combine(datetime.date.today(), heure_reservation) - datetime.timedelta(hours=1)).time()
        
        # Heure de fin (heure + 1 heure)
        heure_fin = (datetime.datetime.combine(datetime.date.today(), heure_reservation) + datetime.timedelta(hours=1)).time()
        
        # Exécuter la requête SQL en utilisant les variables heure_deb et heure_fin
        sql = "SELECT COUNT(*) AS count FROM {} WHERE date = %s AND heure >= %s AND heure <= %s".format(restaurant)
        cursor.execute(sql, (date, heure_deb, heure_fin))
        
        # Récupérer le résultat de la requête
        result = cursor.fetchone()
        print(result)
        print(result[0])
        # Vérifier si le nombre de réservations est supérieur ou égal à 3
        if result[0] >= 3:
            return "0"
        else:
            return "1"
    except pymysql.Error as e:
        print("Erreur lors de l'exécution de la requête :", e)
    finally:
        # Fermer la connexion à la base de données
        conn.close()


 

@app.route('/handle_form_submission', methods=['POST'])
def handle_form_submission():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="restaurant"
    )
    try:
        nom = request.form['name']
        prenom = request.form['prenom']
        num = request.form['num']
        date = request.form['date']
        time = request.form['time']
        place = request.form['nombre']
        clas = request.form['class']
        restaurant = request.form['restaurant']
        reservation_status = verifier_reservations(date, time,restaurant)
        print(reservation_status)
        if reservation_status == "1":
            cursor = connection.cursor()
            old = oldcli(nom, prenom, num, restaurant) + 1
            data = (nom, prenom, num, date, time, place, clas,old)
            query = "INSERT INTO {} (nom, prenom, num, date, heure, place, class,nombre) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)".format(restaurant)
            cursor.execute(query, data)
            connection.commit()
            query = "SELECT id FROM {} WHERE nom=%s AND prenom=%s AND num=%s AND sysdate=%s".format(restaurant)
            current_date_time = datetime.datetime.now()
            cursor.execute(query, (nom, prenom, num, current_date_time.strftime("%Y-%m-%d %H:%M:%S")))
            rows = cursor.fetchall()
            id = None
            for row in rows:
                id = row[0]
            cursor.close()
            connection.close()
            print (id)
            return [render_template('index.html'), id]
        else:
            return [render_template('index.html'), -1]
    except Exception as e:
        print("Erreur :", e)
        return [render_template('index.html'), 0]


@app.route('/anul')
def anul():
    user = "John" 
    return render_template('annulerr.html', user=user)

@app.route("/annuler", methods=['POST'])
def annuler():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="restaurant"
    )
    id = request.form['id']
    number = request.form['number']
    restaurant = request.form['restaurant']
    cursor = connection.cursor()
    query = "DELETE FROM {} WHERE id=%s AND num=%s".format(restaurant)
    cursor.execute(query, (id, number))
    connection.commit()
    if cursor.rowcount == 1:
        annull = "Réservation annulée avec succès"
    else:
        annull = "La réservation n'a pas été trouvée."
    cursor.close()
    connection.close()

    return json.dumps({"annull": annull}), 200, {'Content-Type': 'application/json'}
 
#render_template('popup.html', user=user)
from flask import jsonify

@app.route('/forg')
def forg():
    user = "khalil" 
    return render_template('forget.html', user=user)


@app.route("/commande", methods=["POST"])
def commande():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="restaurant"
    )
    data = request.get_json()
    nom = data["nom"]
    print(nom)
    prenom = data["prenom"]
    print(prenom)
    num = data["num"]
    print(num)
    lieu = data["lieu"]
    print(lieu)
    foods = data["foods"]
    print(foods)
    total_price = data["totalPrice"]
    livreur_numbers = ["0613489112", "0712347575", "0692839405", "0629385893"]
    livreur_num = random.choice(livreur_numbers)   
    
    try:
        with connection.cursor() as cursor:
            # Insert the total price into the "detail" table
            sql1 = "INSERT INTO detail (total,livreur_num, nom_cli, prenom_cli, num_cli, lieu) VALUES (%s, %s, %s, %s, %s,%s)"
            cursor.execute(sql1, (total_price,livreur_num, nom, prenom, num, lieu))
            
            # Get the generated ID from the "detail" table
            detail_id = cursor.lastrowid
            
            # Iterate through the foods and insert each record into the "commande" table
            for food in foods:
                name = food["name"]
                price = food["price"]
                quantity = food["quantity"]
                
                # Execute the SQL INSERT statement
                sql2 = "INSERT INTO commande (nom, price, quantity, id_com) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql2, (name, price, quantity, detail_id))

        # Commit the changes to the database
        connection.commit()
    except Exception as e:
        # Handle any errors that occurred during the database operation
        print("Erreur lors de l'enregistrement de la commande dans la base de données:", e)
        connection.rollback()
    finally:
        # Close the database connection
        connection.close()
    
    return jsonify({"message": "Commande reçue avec succès!", "livreur_num": livreur_num})




@app.route('/livreur')
def livreur():
    user = "khalil"     
    return render_template('livreur.html', user=user)



@app.route('/menu_panda')
def menu_panda():
    user = "khalil"     
    return render_template('menuu.html', user=user)


@app.route("/forget", methods=['POST'])
def forget():
    connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="restaurant"
    )
    try:
        nom = request.form['name']
        prenom = request.form['prenom']
        number = request.form['number']
        restaurant = request.form['restaurant']
        cursor = connection.cursor()
        query = "select id ,nom,prenom,num, date, heure, place, class, nombre FROM {} where nom=%s and prenom=%s and num=%s ".format(restaurant)
        cursor.execute(query, (nom, prenom, number))
        rows = cursor.fetchall()
        id = None
        for row in rows:
            id = row[0]
        cursor.close()
        connection.close()
        if len(rows) == 0:
            ress = "Aucun enregistrement trouvé pour les paramètres donnés"
        else:
            id, nom, prenom,num, date, heure, place, clas, nombre = rows[0]
            ress =  "voici votre information de reservation <br> <br> id : "+str(id)+ "<br> nom : "+str(nom)+"<br> prenom : "+str(prenom)+"<br> numero : "+str(num)+"<br> date : "+str(date)+"<br> heure : "+str(heure)+"<br> Nombre de place : "+str(place)+"<br> Type de table : "+str(clas)
    except Exception as e:
        ress =  "Une erreur s'est produite lors du traitement de votre demande: {}".format(e)
        
    return json.dumps({"ress": ress}), 200, {'Content-Type': 'application/json'}







@app.route('/modifr')
def modifr():
    user = "John" 
    return render_template('popup.html', user=user)

@app.route('/modify', methods=['POST'])
def modify():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="restaurant"
    )
    try:
        id = request.form['id']
        nom = request.form['name']
        prenom = request.form['prenom']
        num = request.form['num']
        date = request.form['date']
        time = request.form['time']
        place = request.form['nombre']
        clas = request.form['class']
        restaurant = request.form['restaurant']
        reservation_status = verifier_reservations(date, time, restaurant)
        if reservation_status == "1":
            cursor = connection.cursor()
            data = (nom, prenom, date, time, place, clas, id, num)
            query = "UPDATE {} SET nom = %s, prenom = %s, date = %s, heure = %s, place = %s, class = %s WHERE id = %s and num = %s".format(
                restaurant)
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
            connection.close()
            repp = "Modification faite avec succès"
        else:
            repp = "Impossible de modifier la réservation. Veuillez saisir un autre horaire."
    except Exception as e:
        repp = "Une erreur s'est produite lors du traitement de votre demande: {}".format(e)
        
    return json.dumps({"annull": repp}), 200, {'Content-Type': 'application/json'}

 
 
 
 
if __name__ == "__main__":
    app.run(debug=True)
    