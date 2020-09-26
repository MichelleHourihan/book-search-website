import os
import requests
from passlib.hash import sha256_crypt
#os.environ.get(postgres://mvworlwvlwmrug:d099452b72df1e5204fc31dba693eb6265915488728ef82ef6950cf9ecf52973@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d1qsttlenoh0oh)

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

 # an additional extension to sessions which allows them
app = Flask(__name__)
                                 # to be stored server-side
                           
 # Check for environment variable
#set DATABASE_URL=postgres://mvworlwvlwmrug:d099452b72df1e5204fc31dba693eb6265915488728ef82ef6950cf9ecf52973@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d1qsttlenoh0oh

if not os.getenv("DATABASE_URL"):
   raise RuntimeError("DATABASE_URL is not set")
    
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")

def index():
    return render_template("index.html")
    
@app.route("/login")

def login():
    if 'email' in session:
        return render_template("welcome.html", email = session['email'])
    return render_template("login.html")
           
    
@app.route("/register")
def register():
     return render_template("register.html")
    
@app.route("/welcome", methods=["GET","POST"])
def welcome():
        email = request.form.get("email")
        pswd = request.form.get("pswd")
        rpswd = request.form.get("rpswd")
        if pswd != rpswd:
            return render_template("error.html", message="Passwords don't match")
        elif db.execute("SELECT * FROM user_name WHERE email = :email", {"email": email}).rowcount > 0:
            return render_template("error.html", message="User already exists.")
        else: 
            db.execute("INSERT INTO user_name (email, pswd) VALUES (:email, :pswd)",
                {"email": email, "pswd": pswd})
            db.commit()
            return render_template("login.html")

@app.route("/welcomeback", methods=["GET","POST"])
def welcomeback():
    session['email'] = request.form.get('email')
    pswd = (request.form.get("pswd"))
    if db.execute("SELECT * FROM user_name WHERE email = :email AND pswd = :pswd", {"email": session["email"], "pswd":pswd}).rowcount > 0:
    #if (sha256_crypt.verify(pswd, "password")== True):
        
        return render_template("welcome.html", email=session['email'])
    else:
        return render_template("error.html", message="invalid login.")
        
        
@app.route("/logout")
def logout():
    session.pop('email', None)
    return render_template("index.html")
    
    
@app.route("/displaybooks", methods=["GET", "POST"])
def displaybooks():
    searchitem = request.form.get("search")
    
    book = db.execute("SELECT * FROM book WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author OR year LIKE :year" , {"isbn": searchitem + '%',"title": '%' + searchitem+'%', "author": '%'+ searchitem +'%', "year": searchitem}).fetchall()
    return render_template("displaybooks.html", book = book)
    
@app.route("/bookreview/<string:book_isbn>")
def bookreview(book_isbn):
    
    book = db.execute("SELECT * FROM book WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Uw8J4LkyHfqfZSp75RKPSw", "isbns": book_isbn})
    data = res.json()
    average= data['books'][0]
    average2= average['average_rating']
    number2=average['work_ratings_count']
    
    #count= data["ratings_count"]
    return render_template("bookreview.html", book = book, average2=average2, number2=number2)