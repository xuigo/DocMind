from DocMind.SuperAdmin.routes import SuperAdmin
from DocMind.errors.routes import errors
from DocMind.Community.routes import Community
from DocMind.WeeklyReport.routes import WeeklyReport
from DocMind.QuarterPlan.routes import QuarterPlan
from DocMind.ProMemDetail.routes import ProMemDetail
from DocMind.ProDetail.routes import ProDetail
from DocMind.DepartMemDetail.routes import DepartMemDetail
from DocMind.DepartDisciplineDetail.routes import DepartDisciplineDetail
from DocMind.DepartAchieveDetail.routes import DepartAchieveDetail
from DocMind.main.routes import main
from DocMind.User.routes import User
from flask import Flask, render_template, url_for, jsonify, session, redirect

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_message_category = 'info'
login_manager.login_message = u'请登陆后再查看！'
login_manager.login_view = 'User.login'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

# configuration of mailbox
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PORT'] = 25
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)
db = SQLAlchemy(app)

app.register_blueprint(User)
app.register_blueprint(main)
app.register_blueprint(DepartAchieveDetail)
app.register_blueprint(DepartDisciplineDetail)
app.register_blueprint(DepartMemDetail)
app.register_blueprint(ProDetail)
app.register_blueprint(ProMemDetail)
app.register_blueprint(QuarterPlan)
app.register_blueprint(WeeklyReport)
app.register_blueprint(Community)
app.register_blueprint(errors)
app.register_blueprint(SuperAdmin)
