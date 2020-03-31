from pybackup import app, db
from flask import render_template, redirect, url_for, request, Response, flash
from pybackup.forms import SetupForm, LoginForm
from os import path, listdir, remove, getcwd
from shutil import rmtree
from pybackup.models import Settings
from passlib import hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename


@app.route('/setup', methods=['POST', 'GET'])
def setup():
    if path.exists(
        path.join(
            getcwd(),
            r"pybackup\site.db")) and path.getsize(
            path.join(
                getcwd(),
                r"pybackup\site.db")) > 0:
        return redirect(url_for('login'))

    form = SetupForm()
    if form.validate_on_submit():
        try:
            if not path.isdir(form.main_dir.data):
                flash("Path is not found")
                return render_template('setup.html', form=form)
        except BaseException as e:
            flash(e)
            return render_template('setup.html', form=form)

        if form.main_dir.data and form.username.data and form.password.data:
            if path.exists(path.join(getcwd(), "sites.db")):
                db.drop_all()
            else:
                db.create_all()

            main_dir = form.main_dir.data
            username = form.username.data
            password = hash.sha256_crypt.encrypt(form.password.data)

            setting = Settings(
                main_dir=main_dir,
                username=username,
                password=password)

            db.session.add(setting)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template('setup.html', form=form)


@app.route("/login", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if path.getsize(path.join(getcwd(), r"pybackup\site.db")) < 1:
        return redirect(url_for('setup'))

    form = LoginForm()
    if form.validate_on_submit():
        setting = Settings.query.first()
        if form.username.data == setting.username and hash.sha256_crypt.verify(form.password.data, setting.password):
            login_user(setting)
            return redirect(url_for("home"))

        else:
            return render_template(
                "login.html",
                title="Login",
                form=form,
                wrong='yes')

    return render_template("login.html", title="Login", form=form, wrong='no')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/viewer/<filepath>')
@login_required
def view(filepath):
    url = request.path
    file_open = open(filepath, 'r')
    file_content = file_open.read().replace('\n', '<br>')
    file_open.close()

    return render_template(
        'viewer.html',
        file_content=file_content,
        file_path=filepath,
        file_name=path.split(filepath)[1],
        url=url)


@app.route('/upload/<dst>', methods=["POST", "GET"])
@login_required
def upload(dst):
    if request.method == "POST":
        if request.files:
            file = request.files["file"]
            filename = secure_filename(file.filename)
            file.save(path.join(dst, filename))
            return redirect(url_for('explore', dir=dst))


try:
    default_exp = app.route(
        '/explorer',
        defaults={
            'dir': Settings.query.first().main_dir})
except BaseException as e:
    default_exp = app.route('/explorer', defaults={'dir': r"C:\\"})


@default_exp
@app.route('/explorer/<dir>')
@login_required
def explore(dir):
    if not dir.startswith(Settings.query.first().main_dir):
        return redirect(url_for('explore', dir=Settings.query.first().main_dir))

    url = request.path

    files = []

    for index, file in enumerate(listdir(dir)):
        full_path = path.join(dir, file)

        size = int(path.getsize(full_path))

        if size >= 1073741824:  # BYTES: 1073741824 --> 1 GB
            size = size / 1073741824
            size_type = 'GB'
        elif size >= 1000000:  # BYTES: 1000000 --> 1 MB
            size = size / 1000000
            size_type = 'MB'
        elif size >= 1000:  # BYTES: 1000 --> 1 KB
            size = size / 1000
            size_type = 'KB'
        else:
            size_type = 'Bytes'

        # 'f' == File | 'o' == fOlder

        if path.isfile(full_path):
            files.append([index, file, full_path, int(size), size_type, 'f'])
            continue

        files.append([index, file, full_path, size, size_type, 'o'])

    return render_template(
        'explorer.html',
        files=files,
        path_dir=dir,
        main_dir=Settings.query.first().main_dir,
        url=url)


@app.route("/home")
@login_required
def home():
    url = request.path
    return render_template('index.html', url=url, username=Settings.query.first().username)


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@app.route('/delete/<file_path>')
@login_required
def delete(file_path):
    if path.isfile(file_path):
        remove(file_path)
    else:
        rmtree(file_path)
    details = path.split(file_path)
    flash(f'"{details[1]}" Is removed from {details[0]}')
    return redirect(url_for('explore', dir=details[0]))


@app.route("/download/<f_path>")
@login_required
def download(f_path):
    file_name = path.split(f_path)[1]
    file_ext, file_path = path.splitext(f_path)
    with open(f_path, 'r') as file:
        data = file.read()
        return Response(
            data,
            mimetype="text/{}".format(file_ext),
            headers={
                "Content-disposition": "attachment; filename={}".format(file_name)})
