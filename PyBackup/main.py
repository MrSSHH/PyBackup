from flask import Flask, render_template, redirect, url_for, send_from_directory, request, make_response
from forms import LoginForm, ConsoleCommand
from os import path, chdir, getcwd, listdir, remove
from shutil import rmtree
from shutil import rmtree


chdir(r"C:\Users\Ben-PC\Documents\Programming\Python\Projects\PyBackup\upload_cloud")

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
            return render_template("login.html", title="Login", form=form, wrong='yes')

    return render_template("login.html", title="Login", form=form, wrong='no')


@app.route('/viewer/<filepath>')
def view(filepath):
    file_open = open(filepath, 'r')
    file_content = file_open.read().split('\n')
    file_open.close()

    return render_template('viewer.html', file_content=file_content, file_path=filepath, file_name=path.split(filepath)[1])

@app.route('/explorer')
def explore():
    files = []
    folders = []
    for index, file in enumerate(listdir()):
        full_path = path.join(getcwd(), file)
        if path.isfile(full_path):
            files.append([index, file, full_path])
        else:
            folders.append([index, file, full_path])
    return render_template('explorer.html', files=files, folders=folders)


@app.route("/home")
def home():
    return render_template('index.html')

@app.route('/delete_folder/<file_path>')
def delete_folder(file_path):
    rmtree(file_path)
    return redirect('/explorer')

@app.route('/delete/<file_path>')
def delete(file_path):
    remove(file_path)
    return redirect('/explorer')


@app.route("/download/<download_file>")  # fix from upload to download
def download(download_file):
    print("aa")
    return send_from_directory(getcwd(), filename=download_file, as_attachment=True)


@app.route("/serverconsole", methods=["POST", "GET"])
def console():
    if not request.referrer:
        return redirect(url_for("login"))
    else:
        global file
        form = ConsoleCommand()
        data = ""
        error = ''
        commands = {"show files": listdir(getcwd()), "help": 'show files\ncd\nremove dir\ndownload'}

        if form.validate_on_submit():
            try:
                command = str(form.console_command.data)
                if 'cd' in command:
                    chdir(path.join(getcwd(), command.split(' ')[1]))

                elif "remove dir" in command:
                    rmtree(path.join(getcwd(), command.split(" ")[2]))

                elif "download" in command:
                    file = command.split(" ")[1]
                    return download(file)

                elif command in commands.keys():
                    data = commands[command]

                else:
                    error = "Command is not found"

            except BaseException as v:
                error = f'{v}'

        return render_template("console.html", title="Console", data=data, form=form, error=error)

if __name__ == "__main__":
    app.run(debug=True)