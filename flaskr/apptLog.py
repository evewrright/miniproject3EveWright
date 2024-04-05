from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('apptLog', __name__)


@bp.route('/')
def index():
    db = get_db()
    appointments = db.execute(
        'SELECT a.id, topic, body, created, occurred, author_id, student_id, s.first_name, s.last_name, username'
        ' FROM appointment a'
        ' JOIN user u ON a.author_id = u.id'
        ' JOIN student s ON a.student_id = s.id'
        ' ORDER BY occurred DESC'
    ).fetchall()
    return render_template('apptLog/index.html', appointments=appointments)


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
                'INSERT INTO appointment (occurred, topic, body, author_id, student_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (occurred, topic, body, g.user['id'], student_id)
            )
            db.commit()
            return redirect(url_for('apptLog.index'))

    return render_template('apptLog/create.html', students=students)


def get_appointment(id, check_author=True):
    appointment = get_db().execute(
        'SELECT a.id, topic, body, created, occurred, author_id, username'
        ' FROM appointment a JOIN user u ON a.author_id = u.id'
        ' WHERE a.id = ?',
        (id,)
    ).fetchone()

    if appointment is None:
        abort(404, f"appointment id {id} doesn't exist.")

    if check_author and appointment['author_id'] != g.user['id']:
        abort(403)

    return appointment


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    appointment = get_appointment(id)

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
                'UPDATE appointment SET occurred = ?, topic = ?, body = ?'
                ' WHERE id = ?',
                (occurred, topic, body, id)
            )
            db.commit()
            return redirect(url_for('apptLog.index'))

    return render_template('apptLog/update.html', appointment=appointment)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_appointment(id)
    db = get_db()
    db.execute('DELETE FROM appointment WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('apptLog.index'))