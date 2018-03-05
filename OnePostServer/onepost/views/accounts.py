import os
import shutil
import tempfile
import hashlib
import uuid
import flask
from flask import request, redirect, url_for, session, abort
import onepost


def sha256sum(filename):
    content = open(filename, 'rb').read()
    sha256_obj = hashlib.sha256(content)
    return sha256_obj.hexdigest()


@onepost.app.route('/accounts/login/', methods=['GET', 'POST'])
def show_login():
    if 'username' in session:
        return redirect(url_for('show_index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = onepost.model.get_db()
        credentials = data.execute('SELECT username, password FROM users \
                                   WHERE username =\'' + username + '\'')
        row = credentials.fetchone()
        if not row:
            return redirect(url_for('show_login'))
        password_db_string = row['password']
        algorithm, salt, password_hash = password_db_string.split("$", 2)
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        if password_hash != hash_obj.hexdigest():
            return redirect(url_for('show_login'))
        session['username'] = username
        return redirect(url_for('show_index'))
    context = {}
    return flask.render_template("login.html", **context)


@onepost.app.route('/accounts/logout/')
def redirect_logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('show_login'))


@onepost.app.route('/accounts/create/', methods=['GET', 'POST'])
def show_create():
    if 'username' in session:
        return redirect(url_for('show_index'))
    if request.method == 'POST':
        # Password
        data = onepost.model.get_db()
        credentials = data.execute('SELECT password FROM users \
                                   WHERE username =\'' + str(request.form['username']) + '\'')
        row = credentials.fetchone()
        if row:
            return redirect(url_for('show_login'))
        password = request.form['password']
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new('sha512')
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join(['sha512', salt, password_hash])
        data = onepost.model.get_db()
        data.execute('INSERT INTO users(username, password) \
            VALUES(?, ?)', [request.form['username'], password_db_string])
        data.commit()
        session['username'] = request.form['username']
        return redirect(url_for('show_index'))
    context = {}
    return flask.render_template("create.html", **context)

