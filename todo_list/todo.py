from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from todo_list.auth import login_required
from todo_list.db import get_db

bp = Blueprint('todo', __name__)


@bp.route('/')
def index():
    # Displays a user's todo list if the user is logged in
    if g.user:
        db = get_db()
        tasks = db.execute(
            'SELECT t.id, title, description, author_id, completed'
            ' FROM todo t JOIN user u ON t.author_id = u.id'
            ' WHERE u.id = ? AND completed = 0',
            (g.user['id'],)
        ).fetchall()
        return render_template('todo/incomplete.html', tasks=tasks)
    else:
        # Displays a welcome page and prompts the user to login
        return render_template('index.html')


@bp.route('/completed', methods=('GET',))
@login_required
def completed():
    """ Displays a page of completed tasks """
    db = get_db()
    tasks = db.execute(
        'SELECT t.id, title, description, author_id, completed'
        ' FROM todo t JOIN user u ON t.author_id = u.id'
        ' WHERE u.id = ? AND completed = 1'
        ' ORDER BY t.id DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('todo/completed.html', tasks=tasks)


@bp.route('/create', methods=('POST',))
@login_required
def create():
    """ Adds posted task to the database """
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


def get_task(id, check_author=True):
    """ Returns a single task from the database """
    task = get_db().execute(
        'SELECT t.id, title, description, completed, author_id'
        ' FROM todo t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_author and task['author_id'] != g.user['id']:
        abort(403)

    return task


@bp.route('/<int:id>/update', methods=('POST',))
@login_required
def update(id):
    """ Updates a tasks title and description in the database """
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
    return redirect(request.referrer)


@bp.route('/<int:id>/dismiss', methods=('POST',))
@login_required
def dismiss(id):
    """ Change a task's status to complete or incomplete """
    post = get_task(id)
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
    """ Deletes a task from the database """
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM todo WHERE id = ?', (id,))
    db.commit()
    return redirect(request.referrer)