from werkzeug.utils import secure_filename

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime
import psycopg2
from os import environ

#Kreira postgre bazu podataka u slucaju da ista ne postoji:
    




app = Flask(__name__)


app.secret_key = 'your secret key'

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "static/uploads/"



db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))




all_entrys = []

current_year = datetime.now().year

with app.app_context():
    
    mydb = psycopg2.connect(user='postgres', password='123', host='diadb', port= '5432')
    
    mydb.autocommit = True
    
    cursor = mydb.cursor()
    
   
    class Users(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True,autoincrement=True)
        email = db.Column(db.String(100), unique=True,)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        datumvreme=db.Column( db.DateTime, nullable=False, default=datetime.utcnow) 
    
    class Orders(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        order_number = db.Column(db.Integer, unique=True,autoincrement=True)
        grupa = db.Column(db.String(100))
        sistem = db.Column(db.String(100))
        objekat = db.Column(db.String(100))
        machine = db.Column(db.String(100))
        tip = db.Column(db.String(100))
        sort = db.Column(db.String(100))
        orderer = db.Column(db.String(100))
        datum = db.Column(db.String(100))
        reliser = db.Column(db.String(100))
        datumvreme=db.Column( db.DateTime, default=datetime.utcnow) 
    
    
    
    
    
    db.create_all()
    
   
    
    mydb = psycopg2.connect(user='postgres', password='123', host='diadb', port= '5432')
    mydb.autocommit = True
    cursor = mydb.cursor()
    
   
    cursor.execute("INSERT INTO Orders(order_number) values (0) ON CONFLICT DO NOTHING;")
    
     
 
    

@app.route('/', methods=["GET", "POST"])
def home():  
    return render_template("index.html", entrys=all_entrys, year=current_year)



@app.route('/index', methods=["GET", "POST"])
def home1():  
    return render_template("index1.html", entrys=all_entrys, year=current_year)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if Users.query.filter_by(email=request.form.get('email')).first():
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = Users(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # login_user(new_user)
        return redirect(url_for("login"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
    
        user = Users.query.filter_by(email=email).first()
        #Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        #Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        #Email exists and password correct
        else:
            login_user(user)
            return redirect(url_for('home1'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/vibrodijagnostika")
def vibro():
    return render_template("vibrodijagnostika.html")


@app.route("/ultrazvuk")
def ultra():
    return render_template("ultrazvuk.html")


@app.route("/centriranje")
def cent():
    return render_template("centriranje.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
   
    mydb = psycopg2.connect(user='postgres', password='123', host='diadb', port= '5432')

    cursor = mydb.cursor()
    # cursor.execute("USE diadb")
    
    
    cursor.execute("SELECT MAX(ID) FROM orders")
    ordernumber = cursor.fetchall()
    
       
    if request.method == "POST" :
        
        new_entry = {
            "order_number": request.form["order_number"],
            "grupa": request.form["grupa"],
            "sistem": request.form["sistem"],
            "objekat" : request.form["objekat"],
            "machine" : request.form["machine"],
            "tip": request.form["tip"],
            "sort": request.form["sort"],
            "orderer" : request.form["orderer"],
            "datum" : request.form["datum"],
            "reliser" : request.form["reliser"]
        }
        all_entrys.append(new_entry)

        new_order = Orders(
            order_number=request.form.get('order_number'),
            grupa=request.form.get('grupa'),
            sistem=request.form.get('sistem'),
            objekat=request.form.get('objekat'),
            machine=request.form.get('machine'),
            tip=request.form.get('tip'),
            sort=request.form.get('sort'),
            orderer=request.form.get('orderer'),
            datum=request.form.get('datum'),
            reliser=request.form.get('reliser')
        )
        db.session.add(new_order)
        db.session.commit()
        
        return redirect(url_for('show'))
    else:  
        return render_template("add.html",year=current_year,ordernumber=ordernumber)


@app.route("/show")
@login_required
def show():
    return render_template("show.html",entrys=all_entrys)


@app.route("/show_permanent",methods=["GET", "POST"])
@login_required
def show_permanent():
    if request.method == "GET":
        query = db.session.query(Orders).all()
    return render_template("show_permanent.html",query=query)


@app.route("/forum")
def forum():
    return render_template("forum.html")



@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name)


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', path="files/cheat_sheet.pdf")


# @app.route('/success', methods = ['POST'])   
# def success():   
#     if request.method == 'POST':   
#         f = request.files['file'] 
#         f.save(f.filename)   
#         return render_template("Acknowledgement.html", name = f.filename)
 

@app.route('/display', methods = ['GET', 'POST'])
def display_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)

        f.save(app.config['UPLOAD_FOLDER'] + filename)

        file = open(app.config['UPLOAD_FOLDER'] + filename,"r",encoding='utf8')
        
        with open("static/uploads", encoding="utf8", errors='ignore') as f:
            content = file.read()   
        
    return render_template('content.html', content=content) 
   
   
@app.route('/ordershow')
def ordershow():
     
      mydb = psycopg2.connect(user='postgres', password='123', host='diadb', port= '5432')
    
      cursor = mydb.cursor()
          
      cursor.execute("SELECT order_number FROM orders")
      ordernumber = cursor.fetchall()
      cursor.execute("SELECT grupa FROM orders")
      grupa = cursor.fetchall()
      cursor.execute("SELECT sistem FROM orders")
      sistem=cursor.fetchall()
      cursor.execute("SELECT objekat FROM orders")
      objekat=cursor.fetchall()
      cursor.execute("SELECT machine FROM orders")
      machine=cursor.fetchall()
      cursor.execute("SELECT tip FROM orders")
      tip=cursor.fetchall()
      cursor.execute("SELECT sort FROM orders")
      sort=cursor.fetchall()
      cursor.execute("SELECT orderer FROM orders")
      orderer=cursor.fetchall()
      cursor.execute("SELECT datum FROM orders")
      datum=cursor.fetchall()
      cursor.execute("SELECT reliser FROM orders")
      reliser=cursor.fetchall()
     
      return render_template("ordershow.html", ordernumber=ordernumber, grupa=grupa, sistem=sistem, objekat=objekat, machine=machine, tip=tip, sort=sort, orderer=orderer, datum=datum, reliser=reliser)

 
# @app.route('/home1')
# def show_home():
#     mydb = mysql.connector.connect(user='root',password='koren',host='localhost',database='diaDB')
#     cursor = mydb.cursor()
#     cursor.execute("select order_number,id from orders")
#     smart_phones=cursor.fetchall()
#     return render_template('home1.html', smart_phones=smart_phones)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        mydb = psycopg2.connect(user='postgres', password='123', host='diadb', port= '5432')
        cursor = mydb.cursor()
        search_value = request.form.get('search_grupe_tipa')
        # print(search_value1)
        # print(type(search_value1))
        
        # search_value=list(search_value1)
        print(search_value)
        print(type(search_value))
        
        cursor.execute("SELECT * FROM orders WHERE lower(grupa) = lower(%s)",(search_value,))
        query=cursor.fetchall()
        print(query)
        print(type(query))
        
        # query1=query[1]
        
        return render_template('search.html', query=query)
    else:
        return render_template('search.html')




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)


# try: 
#     if  __name__ == '__main__':
#         app.run(debug=True,port=4000)
# except:
#     print("Exception occured!")
#     from werkzeug.serving import run_simple
#     run_simple('localhost', 5000, app)


# if __name__=="__main__":
#      app.run(port=5000, debug=True)

# if __name__ == "__main__":
#   app.run(debug=True)  
  
       
# if __name__ == "__main__":
#       app.run(host='0.0.0.0', port=6000)
