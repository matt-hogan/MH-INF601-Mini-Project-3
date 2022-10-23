from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todo_list.auth import login_required
from todo_list.db import get_db

bp = Blueprint('todo', __name__)


@bp.route('/')
def index():
    # Only displays a todo list if the user is logged in
    if g.user:
        db = get_db()
        posts = db.execute(
            'SELECT t.id, title, description, author_id, completed'
            ' FROM todo t JOIN user u ON t.author_id = u.id'
            ' WHERE u.id = ? AND completed = 0',
            (g.user['id'],)
        ).fetchall()
        return render_template('todo/incomplete.html', posts=posts)
    else:
        return render_template('index.html')


@bp.route('/completed', methods=('GET',))
@login_required
def completed():
    db = get_db()
    posts = db.execute(
        'SELECT t.id, title, description, author_id, completed'
        ' FROM todo t JOIN user u ON t.author_id = u.id'
        ' WHERE u.id = ? AND completed = 1',
        (g.user['id'],)
    ).fetchall()
    return render_template('todo/completed.html', posts=posts)


@bp.route('/create', methods=('POST',))
@login_required
def create():
    title = request.form['title']
    description = request.form['description']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO todo (title, description, author_id, completed)'
            ' VALUES (?, ?, ?, 0)',
            (title, description, g.user['id'])
        )
        db.commit()
    return redirect(url_for('todo.index'))


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT t.id, title, description, completed, author_id'
        ' FROM todo t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('POST',))
@login_required
def update(id):
    title = request.form['title']
    description = request.form['description']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'UPDATE todo SET title = ?, description = ?'
            ' WHERE id = ?',
            (title, description, id)
        )
        db.commit()
    return redirect(url_for('todo.index'))


@bp.route('/<int:id>/dismiss', methods=('POST',))
@login_required
def dismiss(id):
    post = get_post(id)
    if post["completed"]:
        completed = 0
    else:
        completed = 1

    db = get_db()
    db.execute(
        'UPDATE todo SET completed = ?'
        ' WHERE id = ?',
        (completed, id)
    )
    db.commit()
    return redirect(request.referrer)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM todo WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('todo.index'))