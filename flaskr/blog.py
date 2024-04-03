from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, topic, body, created, occurred, author_id, student_id, s.first_name, s.last_name, username'
        ' FROM post p'
        ' JOIN user u ON p.author_id = u.id'
        ' JOIN student s ON p.student_id = s.id'
        ' ORDER BY occurred DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    students = db.execute(
        'SELECT id, first_name, last_name FROM student'
    ).fetchall()

    if request.method == 'POST':
        occurred = request.form['occurred']
        topic = request.form['topic']
        body = request.form['body']
        student_id = request.form['student']
        error = None

        if not topic:
            error = 'Topic is required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO post (occurred, topic, body, author_id, student_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (occurred, topic, body, g.user['id'], student_id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html', students=students)


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, topic, body, created, occurred, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        occurred = request.form['occurred']
        topic = request.form['topic']
        body = request.form['body']
        error = None

        if not topic:
            error = 'Topic is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET occurred = ?, topic = ?, body = ?'
                ' WHERE id = ?',
                (occurred, topic, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))