import psycopg2
from flask import Flask, render_template, redirect, request, session
from init_db import *

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/")
def home():
    return  render_template("home.html")

@app.route("/register",methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        # Formdan gelen verileri al
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        surname = request.form["surname"]

        cur.execute('INSERT INTO users (email, password, name, surname)'
                    'VALUES (%s, %s, %s, %s)',
                    (email, password, name, surname)
                    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect("/login", 302)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        # Formdan gelen verileri al
        email = request.form["email"]
        password = request.form["password"]

        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            # Kullanıcı varsa oturumu başlat
            session['logged_in'] = True
            session['user'] = user
            return redirect("/", 302)
        else:
            # Kullanıcı yoksa hata mesajı göster
            return render_template("login.html", error="Invalid email or password")

@app.route("/logout")
def logout():
    # Oturumu sonlandır
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect("/",302)


@app.route("/expenses", methods=["GET"])
def expenses():
    """Manage expenses"""

    return render_template("expenses.html")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)