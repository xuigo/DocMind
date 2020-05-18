from flask_wtf import FlaskForm
from wtforms import fields
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired, ValidationError
from DocMind.models import UserDB


class RegisterForm(FlaskForm):
    username = fields.StringField("昵称", validators=[
                                  DataRequired(message='用户名不能为空'), 
                                  Length(min=2, max=20, message="用户名至少两位")],
                                  render_kw={"placeholder": "请输入昵称"})
    email = fields.StringField("邮箱", validators=[DataRequired(
                                  message='邮箱不能为空'),
                                  Email(message="邮箱格式不正确")],
                                  render_kw={"placeholder": "请输入邮箱"})
    vercode = fields.StringField(validators=[InputRequired(message="验证码错误")])
    role = fields.SelectField("选择角色",
                                  coerce=int,
                                  validators=[DataRequired()],
                                  default=1,
                                  choices=[(1, '项目负责人'), 
                                  (2, '部门总监'), (3, '人事经理'), 
                                  (4, '研发经理'), (5, '技术负责人')])
    password = fields.PasswordField("密码", validators=[DataRequired(
                                  message="密码不能为空"), 
                                  Length(min=6, max=16, message="密码为只允许6-16位")],
                                  render_kw={"placeholder": "请输入密码"})
    re_password = fields.PasswordField("确认密码", validators=[DataRequired(
                                  message="请再次输入密码"), 
                                  EqualTo('password', message="两次输入密码不一致")],
                                  render_kw={"placeholder": "请再次输入密码"})
    submit = fields.SubmitField("点击注册")
    def validate_username(self, username):
        user = UserDB.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("用户名已存在！")
    def validate_email(self, email):
        user = UserDB.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("此邮箱已被注册！")


class LoginForm(FlaskForm):
    email = fields.StringField("邮箱", validators=[DataRequired(
                                  message='邮箱不能为空'), Email(message="邮箱格式不正确")],
                                  render_kw={"placeholder": "请输入邮箱"})
    vercode = fields.StringField(validators=[InputRequired(message="验证码错误")])
    password = fields.PasswordField("密码", validators=[DataRequired(
                                  message="密码不能为空"), Length(min=6, max=16, message="密码为只允许6-16位")],
                                  render_kw={"placeholder": "请输入密码"})
    submit = fields.SubmitField("点击登陆")


class RequestResetForm(FlaskForm):
    email = fields.StringField("邮箱", validators=[DataRequired(
                                  message='邮箱不能为空'), Email(message="邮箱格式不正确")],
                                  render_kw={"placeholder": "请输入邮箱"})
    vercode = fields.StringField(validators=[InputRequired(message="验证码错误")])
    submit = fields.SubmitField("点击找回")

    def validate_email(self, email):
        user = UserDB.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("此邮箱无注册信息，请确认邮箱名称是否正确！")


class ResetPasswordForm(FlaskForm):
    password = fields.PasswordField("密码", validators=[DataRequired(
                                  message="密码不能为空"), Length(min=6, max=16, message="密码为只允许6-16位")],
                                  render_kw={"placeholder": "请输入密码"})
    re_password = fields.PasswordField("确认密码", validators=[DataRequired(
                                  message="请再次输入密码"), EqualTo('password', message="两次输入密码不一致")],
                                  render_kw={"placeholder": "请再次输入密码"})
    submit = fields.SubmitField("点击修改")


class ResetPasswordFormIn(FlaskForm):
    now_password = fields.PasswordField("当前密码", validators=[DataRequired(
                                  message="密码不能为空"), Length(min=6, max=16, message="密码为只允许6-16位")],
                                  render_kw={"placeholder": "请输入密码"})
    password = fields.PasswordField("新密码", validators=[DataRequired(
                                  message="密码不能为空"), Length(min=6, max=16, message="密码为只允许6-16位")],
                                  render_kw={"placeholder": "请输入密码"})
    re_password = fields.PasswordField("确认密码", validators=[DataRequired(
                                  message="请再次输入密码"), EqualTo('password', message="两次输入密码不一致")],
                                  render_kw={"placeholder": "请再次输入密码"})
    submit = fields.SubmitField("点击修改")
