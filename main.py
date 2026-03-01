from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '102-537-606'

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

# CREATE DATABASE

class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB



class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        user = User.query.filter_by(
            email=request.form.get('email')
        ).first()

        flash("User already exist")

        if not user:
            new_user = User(
                email=request.form.get('email'),
                name=request.form.get('name'),
                password= generate_password_hash(request.form.get('password'), salt_length=8, method='pbkdf2:sha256')

            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return render_template("secrets.html", name=request.form.get('name'))

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":

        user = User.query.filter_by(
            email=request.form.get('email')
        ).first()

        if not user:
            flash("User does not exist")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, request.form.get("password")):
            flash("Wrong password")
            return redirect(url_for("login"))

        login_user(user)
        return render_template("secrets.html", name=user.name)

    return render_template("login.html")

@app.route('/secrets')
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    logout_user()
    return render_template("login.html")


@app.route('/download', methods=["GET", "POST"])
def download():
    return send_from_directory('static', path="files/cheat_sheet.pdf")



if __name__ == "__main__":
    app.run(debug=True)
