import datetime
import hashlib
import sqlite3

from flask import Flask, request, Response, render_template, g, url_for, session
from werkzeug.utils import secure_filename, redirect

from db import db_init, db
from models import Img

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

DATABASE='C:/Users/PeadC/Desktop/PJATK/Semestr 2/WPRG/Projekt v2/img.db'

app.secret_key="'zajeb_w_klawiature'"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def sth():
    return redirect(url_for('login'))

@app.route('/login', methods=('GET','POST'))
def login():
    if request.method =='POST':
        session.pop('user_id',None)
        username = request.form['username']
        password = request.form['password']
        user= query_db('SELECT id, username, password FROM users where username=?',(username,))
        if user and user[0][2] == password:
            session['user_id']=user[0][0]
            session['username'] = username
            session['timestamp'] = datetime.datetime.now()
            return redirect(url_for('startPage'))
        else:
            return render_template('login.html', login=username, foo=True)

    return render_template('login.html')


@app.route('/startPage', methods=('GET', 'POST'))
def startPage():
    images = query_db('SELECT id FROM img ORDER BY id DESC')
    tmp = []
    for x in images:
        # y='http://127.0.0.1:5000/'
        tmp.append(x[0])
    list = str(tmp).strip('[(,),]')
    list2= []
    list3= []
    for i in images:
        list2.append(i)
    for i in list2:
        list3.append('http://127.0.0.1:5000/'+(str(i).translate({ord(i): None for i in "(,)"})))
    print(list3)
    return render_template('index.html', result_db=list3, user=session['username'])

@app.route('/register', methods=('GET', 'POST'))
def register():
    ist = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        the_same_user = query_db("Select * from users Where username =?", (username,))
        if not the_same_user:
            database = get_db()
            new_user = database.execute("Insert into users (username,password) VALUES (?,?)",(username, password,))
            database.commit()
            new_user.close()
            return redirect(url_for('login'))
        else:
            ist = True
    return render_template('register.html', foo=ist)

@app.route('/logout')
def logout():
    del session['username']
    del session['timestamp']
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()


    return redirect(url_for('startPage'))

@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)