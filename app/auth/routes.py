from app.auth import bp
from app import db
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequest, ResetPasswordForm
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from app.models import User
from flask_babel import _
from app.auth.email import send_password_reset_email

@bp.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember = form.remember_me.data)    
        flash(_('You have logged in successfully!'))
        return redirect(url_for('main.home'))
    return render_template('auth/login.html', title = _('Home'), form = form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('You have been registered successfully! Log in to continue.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title = _('Register'), form = form)

@bp.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title = _('Reset Password'), form = form)

@bp.route('/reset_password_request', methods = ['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetPasswordRequest()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions on how to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title = _('Request Password Reset'), form = form)