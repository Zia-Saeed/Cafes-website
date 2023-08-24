from flask import Flask, redirect, url_for, render_template, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_bootstrap import Bootstrap
from forms import Login, Register, Contact, AddCafe, Review
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import smtplib
from sqlalchemy.orm import relationship
from functools import wraps
import os
from flask_ckeditor import CKEditor
import datetime as dt
from flask_gravatar import Gravatar

APP_PERMISSION = os.environ.get("password")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app=app)
ckeditor = CKEditor(app)
db = SQLAlchemy(app=app)
login_manager = LoginManager()
login_manager.__init__(app=app)


class Cafe(db.Model):
    __tablename__ = "cafe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    review_cafe = relationship("Reviews", back_populates="review_cafe")


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    email = db.Column(db.String(70), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    review_user = relationship("Reviews", back_populates="user_review")


class Reviews(db.Model, UserMixin):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    auth_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey("cafe.id"))
    review = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.String(), nullable=False)
    review_cafe = relationship("Cafe", back_populates="review_cafe")
    user_review = relationship("Users", back_populates="review_user")
    date = db.Column(db.String(200), nullable=False)


# with app.app_context():
#     db.create_all()

@login_manager.user_loader
def login_manager(user_id):
    return Users.query.get(user_id)


def admin_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id == 1:
            return func(*args, **kwargs)
        else:
            return abort(443)
    return wrapper


@app.route("/")
def home():
    cafes = Cafe.query.all()
    return render_template("index.html", cafes=cafes)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    contact = Contact()
    if request.method == "POST" and contact.validate_on_submit():
        if not current_user.is_authenticated:
            flash("To Contact Us please Login or Signup")
            return render_template("contact.html", contact=contact)
        name = contact.name.data
        email = contact.email.data
        message = contact.message.data
        msg = f"Subject:Cafe website contact message\n\nFrom Email:{email}, Name: {name}\nMessage: {message}"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            send_email = "zia.aseh@gmail.com"
            connection.login(
                user=send_email,
                password=APP_PERMISSION,
            )
            connection.sendmail(
                from_addr=send_email,
                to_addrs=send_email,
                msg=msg,
            )
            flash(message="Message sent Successfully")
    return render_template("contact.html", contact=contact)


@app.route("/cafe/<int:id>", methods=["POST", "GET"])
def cafe_detail(id):
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == id)).scalar()
    form = Review()
    gravatar = Gravatar(
        app,
        size=100,
        rating='g',
        default='retro',
        force_default=False,
        force_lower=False,
        use_ssl=False,
        base_url=None
    )
    if request.method == "POST" and form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("To leave a review you must login or Signup")
            return redirect(url_for('login'))
        else:
            new_review = Reviews(
                review = form.body.data,
                date= dt.date.today(),
                auth_id = current_user.id,
                post_id = cafe.id,
            )
            db.session.add(new_review)
            db.session.commit()
            flash("Review add successfully")
    return render_template("cafe_details.html", cafe=cafe, form=form, gravatar=gravatar)


@app.route("/login", methods=["GET", "POST"])
def login():
    login = Login()
    if request.method == "POST" and login.validate_on_submit():
        user = Users.query.filter_by(email=login.email.data).first()
        if user:
            password = check_password_hash(password=login.password.data, pwhash=user.password)
            if password:
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Message Incorrect Password")
                return render_template("login.html")
        else:
            flash("User doesn't exits")
    return render_template("login.html", login=login)


@app.route("/register", methods=["GET", "POST"])
def register():
    register = Register()
    if request.method == "POST" and register.validate_on_submit():
        user = db.session.execute(db.select(Users).where(Users.email == register.email.data)).scalar()
        if user:
            flash(f"You have already Signup with this {register.email.data}.Login Instead")
            return redirect(url_for('login'))
        else:
            password = generate_password_hash(register.password.data, method="pbkdf2:sha256", salt_length=8)
            new_user = Users(
                name=register.name.data,
                email=register.email.data,
                password=password
            )

            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("register.html", register=register)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/newcafe", methods=["POST", "GET"])
@login_required
@admin_auth
def add_new_cafe():
    new_cafe = AddCafe()
    toilets = 1 if new_cafe.toilet.data == "True" else 0
    wifi = 1 if new_cafe.wifi.data == "True" else 0
    sockets = 1 if new_cafe.sockets.data == "True" else 0
    can_take_calls = 1 if new_cafe.can_take_calls.data == "True" else 0

    if request.method == "POST" and new_cafe.validate_on_submit():
        print(new_cafe.toilet.data)
        new_cafe = Cafe(
            name=new_cafe.name.data,
            map_url=new_cafe.map_url.data,
            img_url=new_cafe.img_url.data,
            location=new_cafe.location.data,
            seats=new_cafe.seats.data,
            coffee_price=f"£{new_cafe.price.data}",
            has_toilet=toilets,
            has_wifi=wifi,
            has_sockets=sockets,
            can_take_calls=can_take_calls,
        )
        db.session.add(new_cafe)
        db.session.commit()
        flash("Cafe Added Successfully")
        return redirect(url_for("add_new_cafe"))
    return render_template("new_cafe.html", cafe=new_cafe)


@app.route("/delete_re/<int:id>")
def delete_review(id):
    review_to_delete = db.session.execute(db.select(Reviews).where(Reviews.post_id == id)).scalar()
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == review_to_delete.post_id)).scalar()
    db.session.delete(review_to_delete)
    db.session.commit()
    return redirect(url_for("cafe_detail", id=cafe.id))


@app.route("/delete")
def delete_cafe():
    cafe_id = request.args.get("id")
    if cafe_id:
        cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        db.session.delete(cafe_to_delete)
        db.session.commit()


@app.route("/update", methods=["GET", "POST"])
def update_cafe():
    cafe = Cafe.query.get(request.args.get("id"))
    update = AddCafe(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        seats=cafe.seats,
        price=cafe.coffee_price,
        sockets=cafe.has_sockets,
        toilet=cafe.has_toilet,
        wifi=cafe.has_wifi,
        can_take_calls=cafe.can_take_calls,
    )
    if request.method == "POST" and update.validate_on_submit():
        toilets = 1 if update.toilet.data == "True" else 0
        wifi = 1 if update.wifi.data == "True" else 0
        sockets = 1 if update.sockets.data == "True" else 0
        can_take_calls = 1 if update.can_take_calls.data == "True" else 0
        cafe.name = update.name.data
        cafe.map_url = update.map_url.data
        cafe.img_url = update.img_url.data
        cafe.location = update.location.data
        cafe.seats = update.seats.data
        cafe.coffee_price = update.price.data
        cafe.has_sockets = sockets
        cafe.has_toilet = toilets
        cafe.has_wifi = wifi
        cafe.can_take_calls = can_take_calls
        db.session.commit()
        flash("Cafe Updated Successfully")
    return render_template("update.html", form=update)


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
