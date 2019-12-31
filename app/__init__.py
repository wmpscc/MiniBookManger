from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os


basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'main.login'
login_manager.login_message = u"请先登录。"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hard to guess string'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:wmpscc@localhost:3306/bookmanage?charset=utf8mb4'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    db.init_app(app)
    db.create_all(app=app)
    login_manager.init_app(app)
    # 附加路由
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
