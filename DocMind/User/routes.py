from flask import render_template, url_for, redirect, request, flash, session
from flask_login import login_user, current_user, login_required, logout_user
from flask_mail import Message
from flask import Blueprint

import DocMind.config.utils as utils
from DocMind.models import *
from DocMind import db, bcrypt, mail
from DocMind.User.forms import RegisterForm, LoginForm, RequestResetForm, ResetPasswordForm, ResetPasswordFormIn
import DocMind.config.DocTemplate as DocTemplates

from flask_mail import Message
import time
import os
import random
import json

User = Blueprint("User", __name__)


@User.route('/login', methods=['POST', 'GET'])
def login():
    user_form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if user_form.validate_on_submit():
        if session['ver_code'] == user_form.vercode.data:  # 验证码判断
            user = UserDB.query.filter_by(email=user_form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, user_form.password.data):
                login_user(user, remember=False)  # 默认记住密码
                if current_user.username == 'admin_docmind':
                    return redirect(url_for('SuperAdmin.noticeManager'))
                return redirect(url_for('main.index'))
            else:
                flash("Oops,密码错误，登陆失败~", 'danger')
                return redirect(url_for('User.login'))
        else:
            flash("Oops,验证码错误~", 'danger')
            return redirect(url_for('User.login'))

    ver_code = utils.gen_verify_num()
    session['ver_code'] = ver_code['answer']
    return render_template('User/login.html',
                           ver_code=ver_code['question'],
                           form=user_form, title='登陆')


@User.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user_form = RegisterForm()
    if user_form.validate_on_submit():
        if session['ver_code'] == user_form.vercode.data:
            hashed_password = bcrypt.generate_password_hash(
                user_form.password.data).decode('utf-8')
            user = UserDB(username=user_form.username.data,
                          email=user_form.email.data,
                          password=hashed_password, role=user_form.role.data)
            db.session.add(user)
            db.session.commit()
            flash("欢迎{}加入DocMind大家庭，请登录！".format(
                user_form.username.data), 'success')
            return redirect(url_for('User.login'))
        else:
            flash("Oops,验证码错误", 'danger')
            return redirect(url_for('User.register'))
    ver_code = utils.gen_verify_num()
    session['ver_code'] = ver_code['answer']
    return render_template('User/register.html', ver_code=ver_code['question'],
                           form=user_form, title='注册')


@User.route('/setting')
@login_required
def setting():
    templates = DocTemplates.templates_vkreport()
    role = current_user.role
    return render_template('User/setting.html', role=role, templates=templates)


@User.route('/setinfo', methods=['POST', 'GET'])
@login_required
def setinfo():
    username = request.form.get('username')  # 昵称
    sex = request.form.get('sex')  # 性别
    department = request.form.get('department')  # 部门
    project = request.form.get('project')
    sign = request.form.get('sign')
    querydata = UserDB.query.filter_by(username=username).first()
    if querydata is not None and current_user.username != username:

        flash('修改失败，用户已存在', 'danger')
        return redirect(url_for('User.setting'))

    current_user.username = username
    current_user.department = department
    current_user.project = project
    current_user.sex = sex
    current_user.sign = sign
    db.session.commit()
    flash("修改成功", 'success')
    return redirect(url_for('main.index'))


@User.route('/avater', methods=['POST', 'GET'])
@login_required
def avater():
    path = '{}/{}/{}'.format('DocMind', 'static', 'avater')  # 注意修改路径
    path2 = '{}/{}'.format('static', 'avater')
    os.makedirs(path, exist_ok=True)
    file = request.files['file']
    name = file.filename
    filename = int(time.time())
    filetype = name.split('.')[-1]
    flag = random.randint(1, 10)
    savepath = '{}/{}_{}.{}'.format(path, filename, flag, filetype)
    readpath = '{}/{}_{}.{}'.format(path2, filename, flag, filetype)
    file.save(savepath)
    current_user.image = readpath
    db.session.commit()
    data = {}
    data['code'] = 0
    return data


@User.route("/forget", methods=['POST', 'GET'])
def forget():
    if current_user.is_authenticated:
        return redirect(url_for('User.setting'))
    user_form = RequestResetForm()
    if user_form.validate_on_submit():
        if session['ver_code'] == user_form.vercode.data:
            user = UserDB.query.filter_by(email=user_form.email.data).first()
            send_reset_email(user)
            flash('已经将重置密码邮件发送到您的邮箱，请及时查收并设置新的密码', 'success')
            return redirect(url_for('User.login'))
        else:
            flash("Oops,验证码错误", 'danger')
    ver_code = utils.gen_verify_num()
    session['ver_code'] = ver_code['answer']
    return render_template('User/forget.html', ver_code=ver_code['question'], form=user_form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('关于重置DocMind账号密码的邮件', sender='wave_dss@163.com',
                  recipients=[user.email])
    msg.body = '请点击链接进行密码重置操作:\n {} \n\n\n  ————————————————————如果你没有进行重置操作却收到这封邮件，您的邮箱信息可能被冒用，请尽快修改密码————————————————————'.format(
        url_for('User.reset_token', token=token, _external=True))
    mail.send(msg)


@User.route("/reset_token/<token>", methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('User.setting'))
    user = UserDB.verify_reset_token(token)
    if user is None:
        flash('您的验证标识不正确，请重试！', 'warning')
        return redirect(url_for('User.forget'))
    user_form = ResetPasswordForm()
    if user_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            user_form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('您的密码已成功修改，欢迎再次回到DocMind~', 'success')
        return redirect(url_for('User.login'))
    return render_template('User/reset_password.html', form=user_form)


@User.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@User.route('/home')
@login_required
def home():
    print('current_role:{}'.format(current_user.role))
    print('*'*10)
    return render_template('User/home.html')


@User.route('/message')
@login_required
def message():
    return render_template('User/message.html')


@User.route('/repass', methods=['POST', 'GET'])
@login_required
def repass():
    nowpass = request.form.get('nowpass')
    newpass = request.form.get('pass')
    repass = request.form.get('repass')
    if bcrypt.generate_password_hash(nowpass).decode('utf-8') != current_user.password:
        flash('当前密码输入错误，请重新输入！', 'danger')
        return redirect(url_for('User.setting'))
    if newpass != repass:
        flash('两次输入密码不一致，请重新输入！', 'danger')
        return redirect(url_for('User.setting'))
    if len(newpass) not in range(6, 17):
        flash('密码必须具有6-16个字符！', 'danger')
        return redirect(url_for('User.setting'))
    current_user.password = bcrypt.generate_password_hash(
        nowpass).decode('utf-8')
    db.session.commit()
    flash('修改密码成功！', 'success')
    return redirect(url_for('User.setting'))
