import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, request, render_template
import joblib
import mysql.connector
import os

app = Flask(__name__)
model = joblib.load(open('model.pkl', 'rb'))
cv = joblib.load(open('cv.pkl', 'rb'))
 
myDb = mysql.connector.connect(
    host= 'sql12.freesqldatabase.com',
    user= 'sql12664905',
    database= 'sql12664905',
    password= 'THHdlu8bpV',

    #  host='localhost',
    #  user='root',
    #  password='',
    #  database='capstone'

    # host='https://auth-db536.hstgr.io/',
    # user='u622668951_fortcoffee',
    # password='Fortcoffee@123',
    # database='u622668951_fortcoffee'
)

if (myDb.is_connected()):
    print('connected!')
else:
    print('not connected')
    
def fetchAndUpdateAnalytics():
    if os.path.exists('static/sentiments.png'):
        os.remove('static/sentiments.png')

    mycursor = myDb.cursor()
    mycursor.execute("SELECT * FROM reviews")    
    myresult = mycursor.fetchall()

    mycursor.close()

    positive = []
    negative = []

    for row in myresult:
        if bool(row[3]):
            positive.append(row[1])
        else:
            negative.append(row[1])

    if len(positive) > 0 or len(negative) > 0:
        y = np.array([len(positive), len(negative)])
        mylabels = ["Positive", "Negative"]
        
        explode = (0.1, 0.0)

        plt.close()

        plt.pie(y, labels = mylabels, autopct='%1.1f%%', colors=["#5dbb63", "tomato"], shadow = True, explode = explode)
        plt.legend(title = "Customer's Sentiments : -")
        plt.savefig('static/sentiments.png')
        plt.switch_backend('agg')
    
    return myresult

@app.route('/')
def home():
    myresult = fetchAndUpdateAnalytics()
    return render_template('index.html', myresult=myresult)


@app.route('/predict', methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''

    if request.method == 'POST':
        text = request.form['review']
        data = [text]
        vectorizer = cv.transform(data).toarray()
        prediction = model.predict(vectorizer)

        mycursor = myDb.cursor()
        
        sql = "INSERT INTO reviews (review, sentiment) VALUES (%s, %s)"
        value = (text, bool(prediction[0]))

        mycursor.execute(sql, value)

        myDb.commit()
        
        mycursor.close()
        
        myresult= fetchAndUpdateAnalytics()
    
        if prediction:
            return render_template('index.html', prediction_text='The review is Positive', myresult=myresult)
        else:
            return render_template('index.html', prediction_text='The review is Negative.', myresult=myresult)
        
@app.route('/login', methods=['POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        mycursor = myDb.cursor()
        
        sql = "SELECT * FROM users WHERE username=%s AND password=%s"
        value = (username, password)

        mycursor.execute(sql, value)
        data = []
        fetchedData = mycursor.fetchone()
        if fetchedData:
            data = fetchedData

        mycursor.close()
        
        myresult= fetchAndUpdateAnalytics()
    
        if len(data) > 0:
            return render_template('index.html', login=True  , myresult=myresult)
        else:
            return render_template('index.html', login=False , myresult=myresult)

@app.route('/logout', methods=['POST'])
def logout():
    myresult= fetchAndUpdateAnalytics()
    return render_template('index.html', login=False  , myresult=myresult)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
