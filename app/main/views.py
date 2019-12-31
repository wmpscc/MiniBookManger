from . import main
from .forms import Login, Logon, SearchBookForm, StoreForm, NewStoreForm, UpdateStoreForm, BorrowForm, \
    SearchStudentForm, BookDelete, ChangeUserInfo, BookBookForm
from ..models import Admin, Student, Book, Inventory, ReadBook
from .. import db
from flask import flash, redirect, url_for, session, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import time
from datetime import datetime, date


# ******************************* 注册登录相关 *******************************

@main.route('/', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = Admin.query.filter_by(admin_id=form.account.data, password=form.password.data).first()
        user_2 = Student.query.filter_by(card_id=form.account.data, password=form.password.data).first()
        if user is None and user_2 is None:
            flash(u'用户名或密码错误，请重新输入')
            return redirect(url_for('.login'))  # 蓝图跳转
        else:
            if user is not None:
                login_user(user)
                print("login------>", user)
                session['admin_id'] = user.admin_id
                session['name'] = user.admin_name
                session['right'] = '最高管理功能'
                session['group'] = 'admin'
                current_user.right = session['right']
                current_user.group = session['group']


            else:
                login_user(user_2)
                print("login------>", user_2)
                session['admin_id'] = user_2.card_id
                session['name'] = user_2.admin_name
                session['right'] = '编辑个人信息 查询/预定图书'
                session['group'] = 'student'
                current_user.right = session['right']
                current_user.group = session['group']
                current_user.sex = user_2.sex
                current_user.telephone = user_2.telephone
                current_user.enroll_date = user_2.enroll_date
                current_user.valid_date = user_2.valid_date

            print(session['name'], session['admin_id'])
            return redirect(url_for('main.index'))
    return render_template('main/login.html', form=form)


@main.route("/logon", methods=['GET', 'POST'])
def logon():
    form = Logon()
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            flash(u"请确认密码是否保持一致！")
        else:
            if form.level.data == '管理员':
                user = Admin(form.account.data, form.name.data, form.password1.data, form.level.data)
                db.session.add(user)
                db.session.commit()
            elif form.level.data == "普通用户":
                card_id = form.account.data
                today_date = date.today()
                today_str = today_date.strftime("%Y-%m-%d")
                today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
                valid_date = (int(today_stamp) + 365 * 4 * 86400) * 1000
                user = Student(card_id, form.account.data, form.password1.data, form.name.data, '男', '12300000000',
                               today_stamp, valid_date, False, False)
                db.session.add(user)
                db.session.commit()
            else:
                flash(u'请正确输入等级！')
                return redirect(url_for('.logon'))

            flash(u'注册成功，请登录！')
            return redirect(url_for('.login'))
    return render_template('main/logon.html', form=form)


@main.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchBookForm()
    return render_template('main/index.html', form=form)


@main.route('/user/<id>')
@login_required
def user_info(id):
    user = Admin.query.filter_by(admin_id=id).first()
    if user is None:
        user = Student.query.filter_by(admin_id=id).first()
    return render_template('main/user-info.html', user=user, name=session.get('name'))


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经登出！')
    return redirect(url_for('.login'))


# ******************************* 查找书籍 *******************************

@main.route('/search_book', methods=['GET', 'POST'])
@login_required
def search_book():  # 这个函数里不再处理提交按钮，使用Ajax局部刷新
    form = SearchBookForm()
    return render_template('main/search-book.html', name=session.get('name'), form=form)


@main.route('/books', methods=['POST'])
def find_book():
    def find_name():
        return Book.query.filter(Book.book_name.like('%' + request.form.get('content') + '%')).all()

    def find_author():
        return Book.query.filter(Book.author.contains(request.form.get('content'))).all()

    def find_class():
        return Book.query.filter(Book.class_name.contains(request.form.get('content'))).all()

    def find_isbn():
        return Book.query.filter(Book.isbn.contains(request.form.get('content'))).all()

    def find_book_location():
        return Book.query.filter(Book.book_location.contains(request.form.get('content'))).all()

    def find_book_store_count():
        return Book.query.filter(Book.store_count.contains(request.form.get('content'))).all()

    methods = {
        'book_name': find_name,
        'author': find_author,
        'class_name': find_class,
        'isbn': find_isbn,
        'book_location': find_book_location,
        'store_count': find_book_store_count
    }
    books = methods[request.form.get('method')]()
    data = []
    for book in books:
        count = Inventory.query.filter_by(isbn=book.isbn).count()
        available = Inventory.query.filter_by(isbn=book.isbn, status=True).count()
        # count = str(book.store_count)
        # available = str(int(book.store_count) - int(book.loan_count))
        item = {'isbn': book.isbn, 'book_name': book.book_name, 'press': book.press, 'author': book.author,
                'class_name': book.class_name, 'book_location': book.book_location, 'count': count,
                'available': available}
        if book.withdraw is False:
            data.append(item)
    return jsonify(data)


# ******************************* 添加新书 *******************************

@main.route('/storage', methods=['GET', 'POST'])
@login_required
def storage():
    form = StoreForm()
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    if form.validate_on_submit():
        if session['group'] == 'student':
            flash(u'您无权限操作！')
            return redirect(url_for('.storage'))
        book = Book.query.filter_by(isbn=request.form.get('isbn')).first()
        exist = Inventory.query.filter_by(barcode=request.form.get('barcode')).first()
        if book is None:
            flash(u'添加失败，请注意本书信息是否已录入，若未登记，请在‘新书入库’窗口录入信息。')
        else:
            if len(request.form.get('barcode')) != 6:
                flash(u'图书编码长度错误')
            else:
                if exist is not None:
                    flash(u'该编号已经存在！')
                else:
                    item = Inventory()
                    item.barcode = request.form.get('barcode')
                    item.isbn = request.form.get('isbn')
                    item.admin = current_user.admin_id
                    item.location = request.form.get('location')
                    item.status = True
                    item.withdraw = False
                    today_date = datetime.date.today()
                    today_str = today_date.strftime("%Y-%m-%d")
                    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
                    item.storage_date = int(today_stamp) * 1000
                    db.session.add(item)
                    db.session.commit()
                    flash(u'入库成功！')
        return redirect(url_for('.storage'))
    return render_template('main/storage.html', name=session.get('name'), form=form)


@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    form = NewStoreForm()
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    if form.validate_on_submit():
        if session['group'] == 'student':
            flash(u'您无权限操作！')
            return redirect(url_for('.new_store'))
        if len(request.form.get('isbn')) != 13:
            flash(u'ISBN长度错误')
        else:
            exist = Book.query.filter_by(isbn=request.form.get('isbn')).first()
            if exist is not None:
                flash(u'该图书信息已经存在，请核对后再录入；或者填写入库表。')
            else:
                book = Book()
                book.isbn = request.form.get('isbn')
                book.book_name = request.form.get('book_name')
                book.press = request.form.get('press')
                book.author = request.form.get('author')
                book.class_name = request.form.get('class_name')
                book.book_location = request.form.get('book_location')
                book.store_count = request.form.get('store_count')
                book.loan_count = 0
                db.session.add(book)
                db.session.commit()

                for i in range(int(book.store_count)):
                    print(i)
                    inventory = Inventory()
                    inventory.barcode = str(book.isbn + '_' + str(i))[-6:]
                    inventory.isbn = book.isbn
                    inventory.admin = current_user.admin_id
                    print(current_user.admin_id)
                    inventory.location = book.book_location
                    inventory.status = True
                    inventory.withdraw = False
                    today_date = date.today()
                    today_str = today_date.strftime("%Y-%m-%d")
                    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
                    inventory.storage_date = today_stamp
                    db.session.add(inventory)
                db.session.commit()

                flash(u'图书信息添加成功！')
        return redirect(url_for('.new_store'))
    return render_template('main/new-store.html', name=session.get('name'), form=form)


# ******************************* 管理书籍信息 *******************************

@main.route('/update_store', methods=['GET', 'POST'])
@login_required
def update_store():
    form = UpdateStoreForm()
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    if form.validate_on_submit():
        form = UpdateStoreForm()
        if session['group'] == 'student':
            flash(u'您无权限操作！')
            return redirect(url_for('.update_store'))
        if len(request.form.get('isbn')) != 13:
            flash(u'ISBN长度错误')
        else:
            exist = Book.query.filter_by(isbn=request.form.get('isbn')).first()
            if exist is None:
                flash(u'该图书信息不存在，请先录入该书信息。')
            else:
                exist.isbn = request.form.get('isbn')
                exist.book_name = request.form.get('book_name')
                exist.press = request.form.get('press')
                exist.author = request.form.get('author')
                exist.class_name = request.form.get('class_name')
                exist.book_location = request.form.get('book_location')
                exist.store_count = request.form.get('store_count')
                exist.loan_count = request.form.get('loan_count')
                db.session.commit()
                flash(u'图书信息修改成功！')
        return redirect(url_for('.update_store'))
    return render_template('main/book-manage.html', name=session.get('name'), form=form)


@main.route('/delete_book', methods=['GET', 'POST'])
@login_required
def delete_book():
    form = BookDelete()
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    if form.validate_on_submit():
        if session['group'] == 'student':
            flash(u'您无权限操作！')
            return redirect(url_for('.delete_book'))
        book = Book.query.filter_by(isbn=request.form.get('isbn'), book_name=request.form.get('book_name')).first()

        if book is None:
            flash(u'该图书信息不存在,请检查信息是否正确！')
        else:
            book.withdraw = True
            db.session.commit()
            exists = Inventory.query.filter_by(isbn=request.form.get('isbn'))
            if exists.first() is not None:
                for inv in exists:
                    inv.status = False
                    inv.withdraw = True
                    db.session.commit()
            flash(u'图书删除成功！')
        return redirect(url_for('.delete_book'))
    return render_template('main/delete-book.html', form=form)


# ******************************* 借书 *******************************

@main.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    form = BorrowForm()
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    return render_template('main/borrow.html', name=session.get('name'), form=form)


@main.route('/out', methods=['GET', 'POST'])
@login_required
def out():
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    barcode = request.args.get('barcode')
    card = request.args.get('card')
    book_name = request.args.get('book_name')
    readbook = ReadBook()
    readbook.barcode = barcode
    readbook.card_id = card
    readbook.start_date = int(today_stamp) * 1000
    readbook.due_date = (int(today_stamp) + 30 * 86400) * 1000
    readbook.borrow_admin = current_user.admin_id
    db.session.add(readbook)
    db.session.commit()
    book = Inventory.query.filter_by(barcode=barcode).first()
    book.status = False
    db.session.add(book)
    db.session.commit()
    bks = db.session.query(Book).join(Inventory).filter(Book.book_name.contains(book_name), Inventory.status == 1). \
        with_entities(Inventory.barcode, Book.isbn, Book.book_name, Book.author, Book.press).all()
    data = []
    for bk in bks:
        item = {'barcode': bk.barcode, 'isbn': bk.isbn, 'book_name': bk.book_name,
                'author': bk.author, 'press': bk.press}
        data.append(item)
    return jsonify(data)


# 预定图书信息
@main.route('/out2', methods=['GET', 'POST'])
@login_required
def out2():
    book_name = request.args.get('book_name')
    print(book_name)
    bks = Book.query.filter_by(book_name=book_name)
    data = []
    for bk in bks:
        item = {'isbn': bk.isbn, 'book_name': bk.book_name,
                'author': bk.author, 'press': bk.press}
        data.append(item)
    return jsonify(data)


@main.route('/find_stu_book', methods=['GET', 'POST'])
def find_stu_book():
    stu = Student.query.filter_by(card_id=request.form.get('card')).first()
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    if stu is None:
        return jsonify([{'stu': 0}])  # 没找到
    if stu.debt is True:
        return jsonify([{'stu': 1}])  # 欠费
    if int(stu.valid_date) < int(today_stamp) * 1000:
        return jsonify([{'stu': 2}])  # 到期
    if stu.loss is True:
        return jsonify([{'stu': 3}])  # 已经挂失
    books = db.session.query(Book).join(Inventory).filter(Book.book_name.contains(request.form.get('book_name')),
                                                          Inventory.status == 1).with_entities(Inventory.barcode,
                                                                                               Book.isbn,
                                                                                               Book.book_name,
                                                                                               Book.author, Book.press). \
        all()
    data = []
    for book in books:
        item = {'barcode': book.barcode, 'isbn': book.isbn, 'book_name': book.book_name,
                'author': book.author, 'press': book.press}
        data.append(item)
    return jsonify(data)


# 查询当前用户借书信息
@main.route('/find_stu_book2', methods=['GET', 'POST'])
def find_stu_book2():
    stu = Student.query.filter_by(card_id=session['admin_id']).first()
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    if stu is None:
        return jsonify([{'stu': 0}])  # 没找到
    if stu.debt is True:
        return jsonify([{'stu': 1}])  # 欠费
    if int(stu.valid_date) < int(today_stamp) * 1000:
        return jsonify([{'stu': 2}])  # 到期
    if stu.loss is True:
        return jsonify([{'stu': 3}])  # 已经挂失
    books = db.session.query(Book).join(Inventory).filter(Book.book_name.contains(request.form.get('book_name')),
                                                          Inventory.status == 1).with_entities(Inventory.barcode,
                                                                                               Book.isbn,
                                                                                               Book.book_name,
                                                                                               Book.author, Book.press). \
        all()
    data = []
    for book in books:
        item = {'barcode': book.barcode, 'isbn': book.isbn, 'book_name': book.book_name,
                'author': book.author, 'press': book.press}
        data.append(item)
    return jsonify(data)


# ******************************* 还书 *******************************

@main.route('/return', methods=['GET', 'POST'])
@login_required
def return_book():
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    form = SearchStudentForm()
    return render_template('main/return.html', name=session.get('name'), form=form)


@main.route('/in', methods=['GET', 'POST'])
@login_required
def bookin():
    barcode = request.args.get('barcode')
    card = request.args.get('card')
    record = ReadBook.query.filter(ReadBook.barcode == barcode, ReadBook.card_id == card, ReadBook.end_date.is_(None)). \
        first()
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    record.end_date = int(today_stamp) * 1000
    record.return_admin = current_user.admin_id
    db.session.add(record)
    db.session.commit()
    book = Inventory.query.filter_by(barcode=barcode).first()
    book.status = True
    db.session.add(book)
    db.session.commit()
    bks = db.session.query(ReadBook).join(Inventory).join(Book).filter(ReadBook.card_id == card,
                                                                       ReadBook.end_date.is_(None)).with_entities(
        ReadBook.barcode, Book.isbn, Book.book_name, ReadBook.start_date,
        ReadBook.due_date).all()
    data = []
    for bk in bks:
        start_date = timeStamp(bk.start_date)
        due_date = timeStamp(bk.due_date)
        item = {'barcode': bk.barcode, 'isbn': bk.isbn, 'book_name': bk.book_name,
                'start_date': start_date, 'due_date': due_date}
        data.append(item)
    return jsonify(data)


@main.route('/find_not_return_book', methods=['GET', 'POST'])
def find_not_return_book():
    stu = Student.query.filter_by(card_id=request.form.get('card')).first()
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    if stu is None:
        return jsonify([{'stu': 0}])  # 没找到
    if stu.debt is True:
        return jsonify([{'stu': 1}])  # 欠费
    if int(stu.valid_date) < int(today_stamp) * 1000:
        return jsonify([{'stu': 2}])  # 到期
    if stu.loss is True:
        return jsonify([{'stu': 3}])  # 已经挂失
    books = db.session.query(ReadBook).join(Inventory).join(Book).filter(ReadBook.card_id == request.form.get('card'),
                                                                         ReadBook.end_date.is_(None)).with_entities(
        ReadBook.barcode, Book.isbn, Book.book_name, ReadBook.start_date,
        ReadBook.due_date).all()
    data = []
    for book in books:
        start_date = timeStamp(book.start_date)
        due_date = timeStamp(book.due_date)
        item = {'barcode': book.barcode, 'isbn': book.isbn, 'book_name': book.book_name,
                'start_date': start_date, 'due_date': due_date}
        data.append(item)
    return jsonify(data)


def timeStamp(timeNum):
    if timeNum is None:
        return timeNum
    else:
        timeStamp = float(float(timeNum) / 1000)
        timeArray = time.localtime(timeStamp)
        print(time.strftime("%Y-%m-%d", timeArray))
        return time.strftime("%Y-%m-%d", timeArray)


# ******************************* 学生信息查询 *******************************
@main.route('/search_student', methods=['GET', 'POST'])
@login_required
def search_student():
    form = SearchStudentForm()
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    return render_template('main/search-student.html', name=session.get('name'), form=form)


@main.route('/student', methods=['POST'])
def find_student():
    stu = Student.query.filter_by(card_id=request.form.get('card')).first()
    if stu is None:
        return jsonify([])
    else:
        valid_date = timeStamp(stu.valid_date)
        return jsonify([{'name': stu.admin_name, 'gender': stu.sex, 'valid_date': valid_date, 'debt': stu.debt}])


@main.route('/record', methods=['POST'])
def find_record():
    records = db.session.query(ReadBook).join(Inventory).join(Book).filter(ReadBook.card_id == request.form.get('card')) \
        .with_entities(ReadBook.barcode, Inventory.isbn, Book.book_name, Book.author, ReadBook.start_date,
                       ReadBook.end_date, ReadBook.due_date).all()  # with_entities啊啊啊啊卡了好久啊
    data = []
    for record in records:
        start_date = timeStamp(record.start_date)
        due_date = timeStamp(record.due_date)
        end_date = timeStamp(record.end_date)
        if end_date is None:
            end_date = '未归还'
        item = {'barcode': record.barcode, 'book_name': record.book_name, 'author': record.author,
                'start_date': start_date, 'due_date': due_date, 'end_date': end_date}
        data.append(item)
    return jsonify(data)


# ******************************* 个人信息修改 *******************************

@main.route('/change_user_info', methods=['GET', 'POST'])
@login_required
def change_user_info():
    form = ChangeUserInfo()
    if form.validate_on_submit():
        student = Student.query.filter_by(admin_id=session['admin_id']).first()
        if student is None:
            flash(u'非法操作，该学生不存在！')
        else:
            student.admin_name = request.form.get('admin_name')
            student.sex = request.form.get('sex')
            student.telephone = request.form.get('telephone')
            db.session.commit()
            current_user.admin_name = student.admin_name
            current_user.sex = student.sex
            current_user.telephone = student.telephone
            current_user.enroll_date = student.enroll_date
            current_user.valid_date = student.valid_date
            flash(u'信息修改成功！')
        return redirect(url_for('.change_user_info'))
    return render_template('main/change-user-info.html', form=form)


# ******************************* 图书预定 *******************************

@main.route('/book_book', methods=['GET', 'POST'])
@login_required
def book_book():
    form = BookBookForm()
    return render_template('main/book-book.html', name=session.get('name'), form=form)
