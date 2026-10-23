from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL
import os
from dotenv import load_dotenv



load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("KEY").encode("utf-8")
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") + "?timeout=20"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


#Set the form
class CreateCafe(FlaskForm):
    c_name = StringField('Cafe Name', validators=[DataRequired(), Length(max=250)])
    c_map_url = StringField('Google Maps URL', validators=[DataRequired(), URL(), Length(max=250)])
    c_img_url = StringField('Image URL', validators=[DataRequired(), URL(), Length(max=250)])
    c_location = StringField('Location', validators=[DataRequired(), Length(max=250)])
    c_has_sockets = StringField('Has Sockets (0 or 1)', validators=[DataRequired()])
    c_has_toilet = StringField('Has Toilet (0 or 1)', validators=[DataRequired()])
    c_has_wifi = StringField('Has Wifi (0 or 1)', validators=[DataRequired()])
    c_can_take_calls = StringField('Can Take Calls (0 or 1)', validators=[DataRequired()])
    c_seats = StringField('Seats', validators=[DataRequired(), Length(max=30)])
    c_coffee_price = StringField('Coffee Price', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Submit')


# CONFIGURE TABLE
class CafeData(db.Model):
    __tablename__ = "cafe"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[int] = mapped_column(Integer)
    has_toilet: Mapped[int] = mapped_column(Integer)
    has_wifi: Mapped[int] = mapped_column(Integer)
    can_take_calls: Mapped[int] = mapped_column(Integer)
    seats: Mapped[str] = mapped_column(String(30), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(30), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    #Query the database for all the posts. Convert the data to a python list.
    return render_template("index.html")

#Add a route so that you can click on individual posts.
@app.route('/cafe_loc/<cafe_loc>')
def show_cafes(cafe_loc):
    #Retrieve a CafeData from the database based on the post_id
    with app.app_context():
        sel_cafe = db.session.execute(db.select(CafeData).where(CafeData.location == cafe_loc)).scalars().all()
    return render_template("cafes_loc.html", all_cafes=sel_cafe, location=cafe_loc)



#delete_post() to remove a blog post from the database
@app.route('/delete/<int:cafe_id>', methods=['GET', 'POST'])
def delete(cafe_id):
    cafe_del = db.get_or_404(CafeData, cafe_id)
    db.session.delete(cafe_del)
    db.session.commit()
    return redirect(url_for('home'))

# Below is the code from previous lessons. No changes needed.
@app.route("/addcity", methods=['GET', 'POST'])
def addcity():
    form = CreateCafe()
    if form.validate_on_submit():
        new_cafe = CafeData(
            name=form.c_name.data,
            map_url=form.c_map_url.data,
            img_url=form.c_img_url.data,
            location=form.c_location.data,
            has_sockets=int(form.c_has_sockets.data),
            has_toilet=int(form.c_has_toilet.data),
            has_wifi=int(form.c_has_wifi.data),
            can_take_calls=int(form.c_can_take_calls.data),
            seats=form.c_seats.data,
            coffee_price=form.c_coffee_price.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("addcity.html", form=form)


@app.route("/cities")
def cities():
    with app.app_context():
        result = db.session.execute(db.select(CafeData).order_by(CafeData.location)).scalars().all()
    locations = sorted(set(cafe.location for cafe in result))
    return render_template("cities.html", all_cafes=result, loc=locations)


if __name__ == "__main__":
    app.run(debug=True, port=5003)