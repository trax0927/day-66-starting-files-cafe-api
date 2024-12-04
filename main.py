from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)
API_KEY = "POSTMALONE_IFALLAPART"


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")



# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    # url = input("")
    # response = requests.get(url)
    cafes = Cafe.query.all()
    random_cafe = random.choice(cafes)
    return jsonify(
        cafe=random_cafe.to_dict()
    )


@app.route("/all")
def get_all_cafe():
    cafes = Cafe.query.all()
    all_cafes = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=all_cafes)


@app.route("/search")
def search_location():
    location = request.args.get('loc')
    cafes = Cafe.query.filter_by(location=location).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "sorry we don't have a cafe at that location"})

# HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={'message': 'cafe added successfully!'})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=["PATCH"])
def update(cafe_id):

    cafe_price_update = Cafe.query.get_or_404(cafe_id)
    if cafe_id:
        cafe_price_update.coffee_price = request.form.get('new_price')
        db.session.commit()
        return jsonify(response={'message': 'cafe added successfully!'})
    else:
        return jsonify(error={"Not Found": "sorry a cafe with that id was not found in the database"})


# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def deleting_cafe(cafe_id):
    delete_cafe = Cafe.query.get_or_404(cafe_id)
    get_api_key = request.args.get('api_key')
    if cafe_id:
        if get_api_key == API_KEY:
            db.session.delete(delete_cafe)
            db.session.commit()

            return jsonify(success={"message": f"Cafe with ID {cafe_id} has been successfully deleted"}), 200
        else:
            return jsonify(error={"access denied": "please ensure you have the right api key"})
    else:
        return jsonify(error={"Not found": "sorry a cafe with that id was not found in the database"})


if __name__ == '__main__':
    app.run(debug=True)
