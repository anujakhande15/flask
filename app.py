from flask import Flask,render_template,request,redirect,flash,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import uuid
import os





app = Flask(__name__)
app.secret_key = "mysecretkey"

app.config["UPLOAD_FOLDER"] = "static/uploads"

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///data.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db = SQLAlchemy(app)





app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=587
app.config["MAIL_USE_TLS"]=True
app.config["MAIL_USERNAME"]='anukhande15@gmail.com'
app.config['MAIL_PASSWORD']='wctj odkl uclv cgxr'


mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),unique=True,nullable=False)
    email = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(200),nullable=False)    
    reset_token = db.Column(db.String(100), nullable=True)  
    profile_images = db.Column(db.String(200),default="default.png")





class Contact(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    message = db.Column(db.String(200))

@app.route("/")
def home():
    if "user_id" not in session:
        flash("Please loging to access app","warning")
        return redirect("/login")
    
    return render_template("home.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form['username']
        uemail = request.form["email"]
        upass = request.form['password']

        existing_user = User.query.filter_by(email=uemail).first()
        if existing_user:
            flash("Email already exists! Please try logging in", "warning")
            return redirect("/login")
        
        hash_pass = generate_password_hash(upass)
        new_data = User(username=uname, email=uemail, password=hash_pass)
        db.session.add(new_data)
        db.session.commit()
        flash("Account created successfully! Please login", "success")
        return redirect("/login")
    
    return render_template("signup.html")





@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome {user.username}", "success")
            return redirect("/")
        else:
            flash("Invalid email or password", "warning")
            return redirect("/login")
    return render_template("login.html")




@app.route("/submit",methods=['POST'])
def submit():

    if "user_id" not in session:
        flash("access to login required","warning")
        return redirect("/login")
    

    name = request.form["username"]
    email = request.form["useremail"]
    message = request.form["usermsg"]

    new_data = Contact(name=name,email=email,message=message)
    db.session.add(new_data)
    db.session.commit()

    msg = Message("New Contact From Submission",
                  sender='anukhande15@gmail.com',
                  recipients=[email])
    msg.body = f"Hello {name},\n\nThank you for contacing us!\n\nYour Message : {message}\n\nWe'll get back to you seen."
    mail.send(msg)

    flash("Data Added successfully !& email send","success")
    return redirect("/show")
    


    


    

@app.route("/show")
def show():

    if "user_id" not in session:
        flash("Plase login to view data","warning")
        return redirect("/login")




    query = request.args.get("query")

    if query:
        contacts = Contact.query.filter(Contact.name.contains(query) | Contact.email.contains(query)).all()
    else:
        contacts = Contact.query.all()
    return render_template("show.html",contacts=contacts)

@app.route("/edit/<int:id>")
def edit(id):
    contact = Contact.query.get_or_404(id)
    return render_template("edit.html",contact=contact)


@app.route("/update/<int:id>",methods=['POST'])
def update(id):
    contact = Contact.query.get_or_404(id)
    contact.name = request.form["username"]
    contact.email = request.form["useremail"]
    contact.message = request.form["usermsg"]
    db.session.commit()
    flash("Data update Successfully !","info")
    return redirect("/show")

@app.route("/delete/<int:id>")
def delete(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash("Data delete successfully!","danger")
    return redirect("/show")


@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = str(uuid.uuid4())  
            user.reset_token = token  
            db.session.commit()

            reset_link = url_for('reset_password', token=token, _external=True)
            print(" RESET LINK:", reset_link) 

            msg = Message("Password Reset Request",
                          sender='anukhande15@gmail.com',
                          recipients=[email])
            msg.body = f"Click the link below to reset your password:\n{reset_link}"
            mail.send(msg)

            flash("Password reset link sent to your email!", "info")
            return redirect("/login")
        else:
            flash("Email not found!", "danger")
    return render_template("forgot.html")



@app.route("/reset/<token>", methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()  

    if not user:
        flash("Invalid or expired reset link!", "danger")
        return redirect("/forgot")

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm']

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(request.url)

        user.password = generate_password_hash(new_password)
        user.reset_token = None  
        db.session.commit()

        flash("Password reset successful! Please login.", "success")
        return redirect("/login")

    return render_template("reset.html", token=token)


@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Plase login first","warning")
        return redirect("/login")
    
    user = User.query.get(session['user_id'])
    return render_template("profile.html",user=user)

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        user.name = request.form["name"]
        user.email = request.form["email"]

        if "profile_image" in request.files:
            file = request.files["profile_image"]
            if file.filename != "":
                filename = secure_filename(file.filename)
                upload_folder = app.config["UPLOAD_FOLDER"]
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filepath = os.path.join(upload_folder,filename)
                file.save(filepath)
                user.profile_images = filename

        db.session.commit()
        flash("Profile Updated Successfully!", "success")
        return redirect("/profile")

    return render_template("edit_profile.html", user=user)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        admin_email = "admin@gmail.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin_pass = generate_password_hash("admin123")
            new_admin = User(username="Admin", email=admin_email, password=admin_pass)
            db.session.add(new_admin)
            db.session.commit()
            print("✅ Admin created: email=admin@gmail.com, password=admin123")










    app.run(debug=True)

















