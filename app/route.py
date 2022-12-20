from app import app, db, bcrypt
from flask import render_template, flash, redirect, url_for, request
from app.models import *
from app.forms import *
from flask_login import login_user, login_required, current_user, logout_user
from app.service.mail import send_reset_email
from app.service.invoice import recognition
from werkzeug.utils import secure_filename

import os
import datetime

TZ_TAIPEI = datetime.timezone(datetime.timedelta(hours=+8))


@app.route('/', methods=['GET','POST'])
@login_required
def index():
    title = 'Home'
    form = PostTweetForm()
    if form.validate_on_submit():
        body = form.text.data
        post = Post(body=body)
        current_user.posts.append(post)
        db.session.commit()
        flash('You have post a new tweet.', category='success')
    follow_data = [len(current_user.followers), len(current_user.followed)]
    page = request.args.get('page', default=1, type=int)
    posts = db.paginate(Post.query.order_by(Post.timestamp.desc()), per_page=2, error_out=False, page=page)
    url_for_page = '/'
    return render_template('index.html', title = title, form=form, follow_data=follow_data, posts=posts, url_for_page=url_for_page)

@app.route('/userpage/<account>')
@login_required
def userpage(account):
    user = User.query.filter_by(account=account).first()
    if user:
        page = request.args.get('page', default=1, type=int)
        clients = db.paginate(Client.query.filter_by(user_id=user.id).order_by(Client.timestamp.desc()), per_page=5, error_out=False, page=page)
        # print(post)
        url_for_page = 'userpage'
        return render_template('userpage.html', user=user, pages=clients, url_for_page=url_for_page)
    else:
        return '404'

@app.route('/follow/<account>')
@login_required
def follow(account):
    user = User.query.filter_by(account=account).first()
    if user:
        current_user.follow(user)
        db.session.commit()
        page = request.args.get('page', default=1, type=int)
        clients = db.paginate(Client.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()), per_page=5, error_out=False, page=page)
        url_for_page = 'userpage'
        return render_template('userpage.html', user=user, pages=clients, url_for_page=url_for_page)
    else:
        return '404'

@app.route('/unfollow/<account>')
@login_required
def unfollow(account):
    user = User.query.filter_by(account=account).first()
    if user:
        current_user.unfollow(user)
        db.session.commit()
        page = request.args.get('page', default=1, type=int)
        posts = db.paginate(Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()), per_page=5, error_out=False, page=page)
        url_for_page = 'userpage'
        return render_template('userpage.html', user=user, posts=posts, url_for_page=url_for_page)
    else:
        return '404'

@app.route('/edit_profile/<account>', methods=['GET','POST'])
@login_required
def edit_profile(account):
    form = UploadPhotoForm()
    user = User.query.filter_by(account=account).first()
    if user:
        page = request.args.get('page', default=1, type=int)
        posts = db.paginate(Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()), per_page=5, error_out=False, page=page)
        url_for_page = 'userpage'
    else:
        return '404'
    if form.validate_on_submit():
        f = form.upload.data
        filename = secure_filename(f.filename)
        full_filename = os.path.join(app.config['APP_DIRECTRY'], 'app', 'static', 'user_avatar', filename)
        f.save(full_filename)
        user.avatar_path = os.path.join('/static', 'user_avatar', filename)
        db.session.commit()
        # print(filename)
        
        return render_template('userpage.html', user=user, posts=posts, url_for_page=url_for_page)
    return render_template('edit_profile.html', form=form)

@app.route('/new_invoice', methods=['GET', 'POST'])
@login_required
def new_invoice():
    title = 'Invoice'
    form = UploadInvoiceForm()
    page = request.args.get('page', default=1, type=int)
    invoices = db.paginate(Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.timestamp.desc()), per_page=2, error_out=False, page=page)
    url_for_page = 'new_invoice'

    if form.validate_on_submit():
        # files = form.upload.data
        # for f in files:
        f = form.upload.data
        path = f.filename
        _, extension = os.path.splitext(path)
        filename = datetime.datetime.now(TZ_TAIPEI).strftime('%Y%m%d_%H%M%S%f') + extension
        full_filename = os.path.join(app.config['APP_DIRECTRY'], 'app', 'static', 'invoices', filename)
        f.save(full_filename)
        filename = os.path.join('/static', 'invoices', filename)
        inovoice = Invoice(path=filename)
        current_user.invoices.append(inovoice)
        db.session.commit()
        return redirect(url_for('new_invoice'))
    return render_template('new_invoice.html', title=title, form=form, items=invoices, url_for_page=url_for_page)

@app.route('/delete_invoice/<id>', methods=['GET', 'POST'])
@login_required
def delete_invoice(id):
    invoice = Invoice.query.filter_by(id=id).first()
    if invoice:
        db.session.delete(invoice)
        db.session.commit()
    return redirect(url_for('new_invoice'))

@app.route('/rec_invoice/<id>', methods=['GET', 'POST'])
@login_required
def rec_invoice(id):
    invoice = Invoice.query.filter_by(id=id).first()
    if invoice and invoice.user_id == current_user.id:
        result = recognition(id)
        invoice.rec_id = result['id']
        invoice.buy_tax_number = result['buy']
        invoice.sell_tax_number = result['sale']
        invoice.time = result['date']
        invoice.price = result['price']
        db.session.commit()
    return redirect(url_for('new_invoice'))



@app.route('/new_client', methods=['GET','POST'])
@login_required
def new_client():
    title = 'Client'
    form = ClientForm()
    page = request.args.get('page', default=1, type=int)
    clients = db.paginate(Client.query.filter_by(user_id=current_user.id).order_by(Client.timestamp.desc()), per_page=2, error_out=False, page=page)
    # print(post)
    url_for_page = 'new_client'
    if form.validate_on_submit():
        tax_number = form.tax_number.data
        name = form.name.data
        code_number = form.code_number.data
        client = Client(tax_number=tax_number, name=name, code_number=code_number)
        current_user.clients.append(client)
        db.session.commit()
        flash('You have add a new client.', category='success')
        return redirect(url_for('new_client'))
    return render_template('new_client.html', form=form, title=title, pages=clients, url_for_page=url_for_page)



@app.route('/delete_client/<client_id>', methods=['GET','POST'])
@login_required
def delete_client(client_id):
    
    client = Client.query.filter_by(id=client_id).first()
    
    if client:
        db.session.delete(client)
        db.session.commit()
    return redirect(url_for('userpage', account=current_user.account))


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        account = form.account.data
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data)
        user = User(account=account, username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registlation Success!', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        account = form.account.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(account=account).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash('Login success', category='info')
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('index'))
        flash('User not exist or password not correct.', category='danger')
    return render_template('login.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/sent_reset_email', methods=['GET','POST'])
def sent_reset_email():
    form = ResetEmailForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = user.generate_reset_token()
        send_reset_email(token, user)
        flash('Password reset requested. Please Check your mailbox.',category='success')
    return render_template('sent_reset_email.html', form = form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.check_reset_token(token)
        if user:
            password = bcrypt.generate_password_hash(form.password.data)
            user.password = password
            db.session.commit()
            flash("Password change applied. You can login with your new password now.", category='success')
            return redirect(url_for('login'))
        else:
            flash("The user does not exist.", category='warning')
    return render_template('reset_password.html', form = form) 