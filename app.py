from flask import Flask,render_template,request,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "mycretkey"

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///data.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    message = db.Column(db.String(200))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/submit",methods=['POST'])
def submit():
    name = request.form["username"]
    email = request.form["useremail"]
    message = request.form["usermsg"]

    new_data = Contact(name=name,email=email,message=message)
    db.session.add(new_data)
    db.session.commit()

    flash("Data Added Successfully !","success")
    return redirect("/show")

@app.route("/show")
def show():
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)