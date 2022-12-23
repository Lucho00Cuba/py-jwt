from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from datetime import timedelta, datetime
import jwt as mjwt
import subprocess

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'jwt.db')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change on production

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

def get_time():
    date_time = datetime.now()
    return date_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

def cmd(command):
    try:
        cmd_result = subprocess.check_call(command, shell=True)
        return cmd_result
    except Exception as e:
        print(f"{e}")
        exit(1)

def json_resp():
    json_return = {}
    json_return['app'] = {
        "name": "py-jwt", 
        "version": "0.0.1", 
        "owner": "justme"
    }
    return json_return

# DB set up and seeders
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped')


@app.cli.command('db_seed')
def db_seed():
    test_user = User(first_name='Super', last_name='Admin', email='super@admin.com', password='super-admin')
    db.session.add(test_user)
    db.session.commit()
    print('Database seeded')

# Planet Routes
@app.route('/', methods=['GET'])
@jwt_required()
def index():
    json_return = json_resp()
    json_return['message'] = "Hello Flask!"
    json_return["datetime"] = get_time()
    return jsonify(json_return)

# User routes
@app.route('/register', methods=['POST'])
def register():
    json_return = json_resp()
    email = request.json['email']
    test = User.query.filter_by(email=email).first()
    if test:
        json_return['message'] = 'that email already exists'
        json_return["datetime"] = get_time()
        return jsonify(json_return), 409
    else:
        params = ['first_name', 'last_name', 'password']
        for elem in params:
            try:
                if request.json[elem] == " ":
                    json_return["message"] = f"{elem} is empty"
                    json_return["datetime"] = get_time()
                    return jsonify(json_return), 400
            except KeyError:
                json_return["message"] = f"not found {elem}"
                json_return["datetime"] = get_time()
                return jsonify(json_return), 400
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        password = request.json['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        json_return["message"] = "user created successfully"
        json_return["datetime"] = get_time()
        return jsonify(json_return), 201


@app.route('/login', methods=['POST'])
def login():
    try:
        if request.is_json:
            email = request.json['email']
            password = request.json['password']

        test = User.query.filter_by(email=email, password=password).first()
        json_return = json_resp()
        if test:
            access_token = create_access_token(identity=email)
            #print(mjwt.decode(access_token, 'super-secret', algorithms=['HS256']))
            json_return['message'] = 'login successful'
            json_return['token'] = access_token
            json_return["datetime"] = get_time()
            return jsonify(json_return)
        else:
            json_return['message'] = 'bad email or password'
            json_return["datetime"] = get_time()
            return jsonify(json_return), 401
    except KeyError:
        json_return["datetime"] = get_time()
        json_return["message"] = "bad requests"
        return jsonify(json_return), 400
    except Exception as e:
        print(e)

# Database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

# DB Schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

# Marsh mellow db adds
user_schema = UserSchema()
users_schema = UserSchema(many=True)

if __name__ == '__main__':
    cmd("flask db_create")
    cmd("flask db_seed")
    app.run(host="0.0.0.0", port=8080)

# JWT
#import jwt
#data = {'some': 'payload'}
#secret = "secret"
#encoded_jwt = jwt.encode(data, secret, algorithm='HS256')
#decoded_jwt = jwt.decode(encoded_jwt, secret, algorithms=['HS256'])
#print(encoded_jwt)
#print(decoded_jwt)