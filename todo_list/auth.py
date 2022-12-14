import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from todo_list.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # Get values from the from
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not first_name:
            error = 'First Name is required.'
        if not last_name:
            error = 'Last Name is required.'
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # Add user to the database
                db = get_db()
                db.execute(
                    "INSERT INTO user (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                    (first_name, last_name, email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"{email} is already registered."
            else:
                # Log in the created user
                user = db.execute(
                    'SELECT * FROM user WHERE email = ?', (email,)
                ).fetchone()
                session.clear()
                # Add the user id as a session cookie to keep the use logged in
                session['user_id'] = user['id']
                return redirect(url_for("index"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Get values from the form and check that user exists
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            error = 'Incorrect email or password'

        if error is None:
            session.clear()
            # Add the user id as a session cookie to keep the use logged in
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """ Gets the current user from the session cookie """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """ Decorator added to routes the user must be logged in to access """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view