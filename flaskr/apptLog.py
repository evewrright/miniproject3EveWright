# INF601 - Advanced Programming in Python
# Eve Wright
# Mini Project 3

#(5/5 points) Initial comments with your name, class and project at the top of your .py file.
#(5/5 points) Proper import of packages used.
#(70/70 points) Using Flask you need to setup the following:
#(10/10 points) Setup a proper folder structure, use the tutorial as an example.
#(20/20 points) You need to have a minimum of 5 pages, using a proper template structure.
#(10/10 points) You need to have at least one page that utilizes a form and has the proper GET and POST routes setup.
#(10/10 points) You need to setup a SQLlite database with a minimum of two tables, linked with a foreign key.
#(10/10) You need to use Bootstrap in your web templates. I won't dictate exactly what modules you need to use but the more practice here the better. You need to at least make use of a modal.
#(10/10) You need to setup some sort of register and login system, you can use the tutorial as an example.
#(5/5 points) There should be a minimum of 5 commits on your project, be sure to commit often!
#(5/5 points) I will be checking out the main branch of your project. Please be sure to include a requirements.txt file which contains all the packages that need installed. You can create this fille with the output of pip freeze at the terminal prompt.
#(10/10 points) There should be a README.md file in your project that explains what your project is, how to install the pip requirements, and how to execute the program. Please use the GitHub flavor of Markdown. Be thorough on the explanations. You will need to explain the steps of initializing the database and then how to run the development server for your project.

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
        'SELECT a.id, topic, body, created, occurred, author_id, student_id, s.first_name, s.last_name, username'
        ' FROM appointment a'
        ' JOIN user u ON a.author_id = u.id'
        ' JOIN student s ON a.student_id = s.id'
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
                'UPDATE appointment SET occurred = ?, topic = ?, body = ?, student_id = ?'
                ' WHERE id = ?',
                (occurred, topic, body, student_id, id)
            )
            db.commit()
            return redirect(url_for('apptLog.index'))

    return render_template('apptLog/update.html', appointment=appointment, students=students)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_appointment(id)
    db = get_db()
    db.execute('DELETE FROM appointment WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('apptLog.index'))