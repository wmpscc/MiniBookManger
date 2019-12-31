from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, EqualTo, Length


class Login(FlaskForm):
    account = StringField(u'账号', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    submit = SubmitField(u'登录')


class Logon(FlaskForm):
    account = StringField(u'账号', validators=[DataRequired(), Length(6, 32)])
    password1 = PasswordField(u'输入密码', validators=[DataRequired(), Length(4, 32)])
    password2 = PasswordField(u'确认密码', validators=[DataRequired(), Length(4, 32)])
    level = StringField(u'输入等级：管理员 or 普通用户', validators=[DataRequired(), Length(3, 4)])
    name = StringField(u'你的名字', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField(u'注册')


class SearchBookForm(FlaskForm):
    methods = [('book_name', '书名'), ('author', '作者'), ('class_name', '类别'), ('isbn', 'ISBN')]
    method = SelectField(choices=methods, validators=[DataRequired()], coerce=str)
    content = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')


class StoreForm(FlaskForm):
    barcode = StringField(validators=[DataRequired(), Length(6)])
    isbn = StringField(validators=[DataRequired(), Length(13)])
    location = StringField(validators=[DataRequired(), Length(1, 32)])
    submit = SubmitField(u'提交')


class BookDelete(FlaskForm):
    isbn = StringField(validators=[DataRequired(), Length(13)])
    book_name = StringField(validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField(u'提交')


class NewStoreForm(FlaskForm):
    isbn = StringField(validators=[DataRequired(), Length(13)])
    book_name = StringField(validators=[DataRequired(), Length(1, 64)])
    press = StringField(validators=[DataRequired(), Length(1, 32)])
    author = StringField(validators=[DataRequired(), Length(1, 64)])
    class_name = StringField(validators=[DataRequired(), Length(1, 64)])
    book_location = StringField(validators=[DataRequired(), Length(1, 64)])
    store_count = StringField(validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField(u'提交')


class UpdateStoreForm(FlaskForm):
    isbn = StringField(validators=[DataRequired(), Length(13)])
    book_name = StringField(validators=[DataRequired(), Length(1, 64)])
    press = StringField(validators=[DataRequired(), Length(1, 32)])
    author = StringField(validators=[DataRequired(), Length(1, 64)])
    class_name = StringField(validators=[DataRequired(), Length(1, 64)])
    book_location = StringField(validators=[DataRequired(), Length(1, 64)])
    store_count = StringField(validators=[DataRequired(), Length(1, 10)])
    loan_count = StringField(validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField(u'提交')


class BorrowForm(FlaskForm):
    card = StringField(validators=[DataRequired()])
    book_name = StringField(validators=[DataRequired()])
    submit = SubmitField(u'搜索')


class SearchStudentForm(FlaskForm):
    card = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')


class ChangeUserInfo(FlaskForm):
    admin_name = StringField(u'你的名字',validators=[DataRequired(), Length(1, 64)])
    sex = StringField(u'男/女', validators=[DataRequired(), Length(1, 2)])
    telephone = StringField(u'联系电话', validators=[DataRequired(), Length(11)])
    submit = SubmitField('保存')

class BookBookForm(FlaskForm):
    book_name = StringField(validators=[DataRequired()])
    submit = SubmitField(u'搜索')
