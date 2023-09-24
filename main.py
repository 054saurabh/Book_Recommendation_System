from flask import Flask,render_template,request
import pickle
from flask_mysqldb import MySQL
import numpy as np
import random


ready=pickle.load(open('ready_df.pkl','rb'))
pre=pickle.load(open('pre_df.pkl','rb'))
books=pickle.load(open('books_df.pkl','rb'))
cosine_similarity=pickle.load(open('model.pkl','rb'))

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'recomended_user'
mysql = MySQL(app)

@app.route('/login_process', methods=['POST'])
def login_process():
    p = 'login.html'
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM saurabh WHERE email = %s AND password = %s", (email, password)) 
        users = cur.fetchone()
        cur.close()
        print(users)
        if users:
            p = 'index.html'
        else:
            p = 'sign_up.html'

    return render_template(p)


@app.route('/signup_process', methods=['POST'])
def signup_process():
    q = 'sign_up.html'
    if request.method == 'POST':
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 == password2:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO saurabh (email, password) VALUES (%s, %s)", (email, password1))
            mysql.connection.commit()
            cur.close()
            q = 'index.html'
        else:
            q = 'sign_up.html'

    return render_template(q)


@app.route('/')
def Home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/book_list')
def book_list():
    count=5
    return render_template('book_list.html',
                           name = list(ready['Book-Title'].values),
                           author=list(ready['Book-Author'].values),
                           image=list(ready['Image-URL-M'].values),
                           nu=count,
                           )


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('sign_up.html')


@app.route('/home_page')
def home_page():
    return render_template('index.html')


@app.route('/result',methods=['POST'])
def result():
    book_name=request.form['book_name']
    print(book_name)
    
    index = np.where(pre.index == book_name)[0][0]
    similar_items = sorted(list(enumerate(cosine_similarity[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pre.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        price=random.randint(1,9)
        item.append(price)
        data.append(item)
    
    return render_template('index.html',data=data)




if __name__=="__main__":
    app.run(debug=True,port=10000)