from flask_login import UserMixin
from sqlalchemy import CheckConstraint

from . import db, login_manager


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(20), primary_key=True)
    admin_name = db.Column(db.String(32))
    password = db.Column(db.String(32))
    level = db.Column(db.String(32))

    def __init__(self, admin_id, admin_name, password, level):
        self.admin_id = admin_id
        self.admin_name = admin_name
        self.password = password
        self.level = level

    def get_id(self):
        return self.admin_id

    def verify_password(self, password):
        if password == self.password:
            return True
        else:
            return False

    def __repr__(self):
        return '<Admin %r>' % self.admin_name


class Student(UserMixin, db.Model):
    __tablename__ = 'student'
    card_id = db.Column(db.String(16), primary_key=True)
    admin_id = db.Column(db.String(20))
    password = db.Column(db.String(32))
    admin_name = db.Column(db.String(32))
    sex = db.Column(db.String(2))
    telephone = db.Column(db.String(11), nullable=True)
    enroll_date = db.Column(db.String(13))  # 入学日期
    valid_date = db.Column(db.String(13))  # 有限期限至
    loss = db.Column(db.Boolean, default=False)  # 是否挂失
    debt = db.Column(db.Boolean, default=False)  # 是否欠费

    def __init__(self, card_id, student_id, password, student_name, sex, telephone, enroll_date, valid_date, loss,
                 debt):
        self.card_id = card_id
        self.admin_id = student_id
        self.password = password
        self.admin_name = student_name
        self.sex = sex
        self.telephone = telephone
        self.enroll_date = enroll_date
        self.valid_date = valid_date
        self.loss = loss
        self.debt = debt

    def get_id(self):
        return self.card_id

    def verify_password(self, password):
        if password == self.password:
            return True
        else:
            return False

    def __repr__(self):
        return '<Student %r>' % self.admin_name


class Book(db.Model):
    __tablename__ = 'book'
    isbn = db.Column(db.String(13), primary_key=True)
    book_name = db.Column(db.String(64))
    author = db.Column(db.String(64))
    press = db.Column(db.String(32))
    class_name = db.Column(db.String(64))
    book_location = db.Column(db.String(64))
    store_count = db.Column(db.Integer)
    loan_count = db.Column(db.Integer)
    withdraw = db.Column(db.Boolean, default=False)  # 是否注销

    def __repr__(self):
        return '<Book %r>' % self.book_name


class Inventory(db.Model):
    __tablename__ = 'inventory'
    barcode = db.Column(db.String(6), primary_key=True)
    isbn = db.Column(db.ForeignKey('book.isbn'))
    storage_date = db.Column(db.String(13))
    location = db.Column(db.String(32))
    withdraw = db.Column(db.Boolean, default=False)  # 是否注销
    status = db.Column(db.Boolean, default=True)  # 是否在馆
    admin = db.Column(db.ForeignKey('admin.admin_id'))  # 入库操作员

    def __repr__(self):
        return '<Inventory %r>' % self.barcode


class ReadBook(db.Model):
    __tablename__ = 'readbook'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    barcode = db.Column(db.ForeignKey('inventory.barcode'), index=True)
    card_id = db.Column(db.ForeignKey('student.card_id'), index=True)
    start_date = db.Column(db.String(13))
    borrow_admin = db.Column(db.ForeignKey('admin.admin_id'))  # 借书操作员
    end_date = db.Column(db.String(13), nullable=True)
    return_admin = db.Column(db.ForeignKey('admin.admin_id'))  # 还书操作员
    due_date = db.Column(db.String(13))  # 应还日期

    def __repr__(self):
        return '<ReadBook %r>' % self.id


@login_manager.user_loader
def load_user(admin_id):
    if Student.query.get(int(admin_id)) is not None:
        print("load----->", Student.query.get(int(admin_id)))
        return Student.query.get(int(admin_id))
    else:
        print("load----->", Admin.query.get(int(admin_id)))
        return Admin.query.get(int(admin_id))
