from flask import Flask, abort, redirect, url_for
app = Flask(__name__)
@app.route('/')
def index():
    print("booba")
    return redirect(url_for('d'))

@app.route('/d')
def login():
    abort(401)
    print("abba")
    this_is_never_executed()


if __name__ == '__main__':
    app.debug = True
    app.run()