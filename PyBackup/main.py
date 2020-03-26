from flask import Flask, render_template, redirect, url_for, request, Response
from forms import LoginForm, ConsoleCommand
from os import path, getcwd, listdir, remove, walk
from shutil import rmtree
import zipfile

main_dir = path.join(getcwd(), 'upload_cloud')
app = Flask(__name__)

app.config['SECRET_KEY'] = 'af7e8e3e25d417f9a0635906dc0325be'


@app.route("/", methods=["POST", "GET"])
def login():
    global userID
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin':
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


@app.route('/explorer', defaults={'dir': main_dir})
@app.route('/explorer/<dir>')
def explore(dir):
    url = request.path

    if not dir.startswith(main_dir) or not request.referrer:
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
        main_dir=main_dir,
        url=url)


@app.route("/home")
def home():
    url = request.path
    return render_template('index.html', url=url)


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


if __name__ == "__main__":
    app.run(debug=True)
