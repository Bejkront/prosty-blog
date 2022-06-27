from flask import Flask, Response, redirect, url_for, request, session, abort, render_template, flash, Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin,login_required, login_user, logout_user,current_user
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


import sqlite3 as sql



conn = sql.connect('blog.db')
print("Opened")
conn.execute('CREATE TABLE IF NOT EXISTS posty (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, tytul TEXT NOT NULL, tresc TEXT NOT NULL, nick TEXT NOT NULL)')
conn.commit()
conn.close()





app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='x#,-\*&^%$qwe-+='
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db = SQLAlchemy(app)

   


    
#class Post(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    text = db.Column(db.Text, nullable=False)
#    data_utw = db.Column(db.DateTime(timezone=True))
#    author = db.Column(db.Integer, db.ForeignKey(
#        'user.id', ondelete="CASCADE"), nullable=False)    
    
    
class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    email = db.Column(db.String(200))
   





@login_manager.user_loader
def get(id):
    return User.query.get(id)

@app.route('/',methods=['GET'])
def main():
    
	return render_template('index.html',tytul='Strona główna')

@app.route('/add_post',methods = ['POST', 'GET'])
def add_post():

 if request.method == 'POST':
 
  now = datetime.now()
  data = now.strftime("%d/%m/%Y %H:%M:%S")
  try:
   
   tytul = request.form['tytulposta']
   tresc = request.form['trescposta']
   nick = current_user.username
   with sql.connect("blog.db") as con:

    cur = con.cursor()
    cur.execute("INSERT INTO posty (data,tytul,tresc,nick) VALUES (?,?,?,?)",(data,tytul,tresc,nick) )
    con.commit()
    msg = "Post został dodany"
  except:
     con.rollback()
     msg = "Nie udało się dodać posta, spróbuj ponownie później"
  finally:
     return render_template("rezultat.html",tytul = 'Dodaj post ',msg = msg)
     con.close()






@app.route('/delpost',methods = ['POST', 'GET'])
def delpost():

 if request.method == 'POST':
  try:
   id = request.form['id']
   with sql.connect("blog.db") as con:

    cur = con.cursor()
    cur.execute("DELETE FROM posty WHERE id =?",(id) )
    con.commit()
    msg = "Post został usunięty"
  except:
     con.rollback()
     msg = "Nie udało się usunąć posta"
  finally:
     return render_template("rezultat.html",tytul = 'Usuwanie posta',msg = msg)
     con.close()




@app.route("/dodaj-post")
@login_required
def new_post():
 	return render_template('utworzpost.html', tytul = 'Dodaj post')

@app.route("/usun-post")
@login_required
def del_post():
 	return render_template('usunpost.html',tytul='Usuń post')


@app.route('/blog')
def blog():

 con = sql.connect("blog.db")
 con.row_factory = sql.Row
 cur = con.cursor()
 cur.execute('SELECT * FROM posty ORDER BY data')
 posty = cur.fetchall();
 return render_template("blog.html",tytul='Blog', posty = posty)


@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return render_template('logout.html', tytul='Wylogowanie')

@app.route('/login',methods=['GET'])
def get_login():
    return render_template('formularz_logowania.html', tytul= 'Zaloguj się')

@app.route('/login', methods=['POST','GET'])
def login_post():

    if request.method == 'POST':
        email= request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            
            login_user(user)
            error = 'Zalogowano'
          
        else:
            error = 'Podałeś niepoprawny email lub hasło'
            
    return render_template("index.html", error=error)
    



@app.route('/signup',methods=['GET'])
def get_signup():
    return render_template('signup.html',tytul='Utwórz nowe konto')

@app.route('/signup',methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password1 = request.form['password1']
    password2 = request.form['password2']

    email_exists = User.query.filter_by(email=email).first()
    username_exists = User.query.filter_by(username=username).first()

    if email_exists:
            error="Podany email jest już przypisany do konta!"
            return render_template('index.html', error=error )
            
    elif username_exists:
            error="Proponowana nazwa jest już zajęta!"
            return render_template('index.html', error=error )
            
    elif password1 != password2:
            error="Hasła nie są identyczne!"  
            return render_template('index.html', error=error )
            
    elif len(username) < 2:
            error="Nazwa musi się składać z minimum 2 znaków!" 
            return render_template('index.html', error=error )
            
    elif len(password1) < 6:
            error="Hasło musi się składać z minimum 6 znaków!"
            return render_template('index.html', error=error )
            
    elif len(email) < 4:
            error="Nieprawidłowy email!"
            return render_template('index.html', error=error )
    else:
        user = User(username=username,email=email,password=password1)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/')




@app.errorhandler(401)
def page_not_found(e):
 tytul=" Oj. Coś poszło nie tak..."
 blad = "401"
 return render_template('blad.html', tytul=tytul, blad=blad)







if __name__ == "__main__":
	app.run(debug=True)
