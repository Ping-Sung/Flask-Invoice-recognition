from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed

from app.models import User

class RegisterForm(FlaskForm):
    account = StringField('Account 帳號名稱', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    username = StringField('Username 會計事務所名稱', validators=[
        DataRequired(),
        Length(max=20)
    ])
    email = StringField('Email 信箱', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password 密碼', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    repeatPassword = PasswordField('Repeat Password 重複密碼', validators=[
        DataRequired(),
        Length(min=8, max=20),
        EqualTo('password')
    ])
    recaptcha = RecaptchaField()
    summit = SubmitField('Register 註冊')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username has been used. 事務所名稱已被註冊')

    def validate_account(self, account):
        user = User.query.filter_by(account=account.data).first()
        if user:
            raise ValidationError('Account has been used. 帳號已被註冊。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email has been used. 信箱已被註冊。')



class LoginForm(FlaskForm):
    account = StringField('Account 帳號', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    password = PasswordField('Password 密碼', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    remember = BooleanField('Remember me 記住帳號')
    summit = SubmitField('Sign in 登入')

class ResetEmailForm(FlaskForm):
    email = StringField('Email 信箱', validators=[
        DataRequired(),
        Email()
    ])
    summit = SubmitField('Comfirm 確認')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email does not exist. 信箱不存在')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password 密碼', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    repeatPassword = PasswordField('Repeat Password 重複密碼', validators=[
        DataRequired(),
        Length(min=8, max=20),
        EqualTo('password')
    ])
    summit = SubmitField('Reset 重置')


class PostTweetForm(FlaskForm):
    text = TextAreaField('Input something 請輸入貼文內容', validators=[
        DataRequired(),
        Length(min=1, max=120)
    ])
    summit = SubmitField('Post 發出貼文')

class UploadPhotoForm(FlaskForm):
    upload = FileField('Upload file', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    summit = SubmitField('Upload 上傳')

class ClientForm(FlaskForm):
    name = StringField('Name 客戶名稱', validators=[
        DataRequired(),
        Length(max=20)
    ])

    tax_number = StringField('Tax number 統一編號', validators=[
        DataRequired(),
        Length(min=8, max=8)
    ])

    code_number = StringField('Code number 文中編號', validators=[
        DataRequired(),
        Length(max=30)
    ])

    summit = SubmitField('Add Client 新增客戶')

    def validate_tax_number(self, tax_number):
        if not tax_number.data.isnumeric():
            raise ValidationError('Tax number only include numbers. 統一編號僅可存在數字')

class UploadInvoiceForm(FlaskForm):
    upload = FileField('Upload Invoice', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    summit = SubmitField('Upload Invoice 上傳發票')