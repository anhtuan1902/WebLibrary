from flask import Flask
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
db = SQLAlchemy(app=app)

app.secret_key = 'HelloWorld'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:12345678@localhost/qltv?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['COMMENT_SIZE'] = 4

# username: admin
# password: 123
babel = Babel(app=app)
login = LoginManager(app=app)


@babel.localeselector
def get_locale():
    return 'vi'


cloudinary.config(
    cloud_name='dzk2a3akv',
    api_key='293869319815116',
    api_secret='L_83MkBlZ3QelvFFIIrH58rYkMM'
)