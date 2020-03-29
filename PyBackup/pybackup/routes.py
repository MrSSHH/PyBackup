from pybackup import app, db
from flask import render_template, redirect, url_for, request, Response, flash
from pybackup.forms import SetupForm, LoginForm
from os import path, listdir, remove, getcwd
from shutil import rmtree
from pybackup.models import Settings


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
                flash("Path Not Found")
                return render_template('setup.html', form=form)
        except EnvironmentError as e:
            flash(e)
            return render_template('setup.html', form=form)

        if form.main_dir.data and form.username.data and form.password.data:
            if path.exists(path.join(getcwd(), "sites.db")):
                db.drop_all()
            else:
                db.create_all()

            setting = Settings(
                main_dir=form.main_dir.data,
                username=form.username.data,
                password=form.password.data)
            db.session.add(setting)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template('setup.html', form=form)


@app.route("/", methods=["POST", "GET"])
def login():
    print(path.join(getcwd(), r"pybackup\site.db"))
    if not path.exists(path.join(getcwd(), r"pybackup\site.db")):
        return redirect(url_for('setup'))
    else:
        if path.getsize(path.join(getcwd(), r"pybackup\site.db")) < 1:
            return redirect(url_for('setup'))

    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == Settings.query.first().username and str(
                form.password.data) == Settings.query.first().password:
            return redirect(url_for("home"))
        else:
            return render_template(
                "login.html",
                title="Login",
                form=form,
                wrong='yes')

    return render_template("login.html", title="Login", form=form, wrong='no')


@app.route('/viewer/<filepath>')
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


try:
    default_exp = app.route(
        '/explorer',
        defaults={
            'dir': Settings.query.first().main_dir})
except BaseException:
    default_exp = app.route('/explorer', defaults={'dir': r"C:\\"})


@default_exp
@app.route('/explorer/<dir>')
def explore(dir):
    url = request.path

    if not dir.startswith(
            Settings.query.first().main_dir) or not request.referrer:
        return redirect(url_for('login'))

    files = []

    for index, file in enumerate(listdir(dir)):
        full_path = path.join(dir, file)

        size = int(path.getsize(full_path))

        if size >= 1073741824:
            size = size / 1073741824
            size_type = 'GB'
        elif size >= 1000000:
            size = size / 1000000
            size_type = 'MB'
        elif size >= 1000:
            size = size / 1000
            size_type = 'KB'
        else:
            size_type = 'Bytes'

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
def home():
    url = request.path
    if not request.referrer:
        return redirect(url_for('login'))
    return render_template('index.html', url=url)


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/delete/<file_path>')
def delete(file_path):
    if path.isfile(file_path):
        remove(file_path)
    else:
        rmtree(file_path)
    return redirect('/explorer')


@app.route("/download/<f_path>")
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
