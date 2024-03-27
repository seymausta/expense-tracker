import psycopg2
from flask import Flask, render_template, redirect, request, session, url_for
from init_db import connect_to_database
from helpers import login_required


app = Flask(__name__)
app.secret_key = "your_secret_key"

conn = connect_to_database()

@app.route("/")
def home():
    return  render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        # Formdan gelen verileri al
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        surname = request.form["surname"]

        try:
            cur = conn.cursor()

            # Kullanıcıyı veritabanına ekle
            cur.execute('INSERT INTO users (email, password, name, surname)'
                        'VALUES (%s, %s, %s, %s)',
                        (email, password, name, surname)
                        )

            conn.commit()

            return redirect("/login", 302)

        except psycopg2.Error as e:
            print("Hata:", e)
            return "Kullanıcı eklenirken bir hata oluştu."

        finally:
            # Bağlantıyı kapat
            if cur:
                cur.close()

    return redirect("/login", 302)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        # Formdan gelen verileri al
        email = request.form["email"]
        password = request.form["password"]

        try:
            cur = conn.cursor()

            # Kullanıcıyı veritabanında sorgula
            cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cur.fetchone()

            if user:
                # Kullanıcı varsa oturumu başlat
                session['logged_in'] = True
                #session['user'] = user
                session['user_id'] = user[0]  # Kullanıcı kimliğini oturum içine kaydet
                return redirect("/", 302)
            else:
                # Kullanıcı yoksa hata mesajı göster
                return render_template("login.html", error="Invalid email or password")

        except psycopg2.Error as e:
            print("Hata:", e)
            return "Giriş yapılırken bir hata oluştu."

        finally:
            # Bağlantıyı kapat
            if cur:
                cur.close()
@app.route("/logout")
def logout():
    # Oturumu sonlandır
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect("/",302)

@app.route('/account')
def account():
    try:
        cur = conn.cursor()

        # Kullanıcı bilgilerini veritabanından al
        user_id = session.get('user_id')
        cur.execute("SELECT name, surname, email FROM users WHERE user_id = %s", (user_id,))
        user_data = cur.fetchone()

        # Kullanıcı bilgilerini temsil eden bir sözlük oluşturun
        user = {
            'name': user_data[0],
            'surname': user_data[1],
            'email': user_data[2]
        }

        return render_template('account.html', user=user)

    except psycopg2.Error as e:
        print("Hata:", e)
        return "Kullanıcı bilgileri alınırken bir hata oluştu."

    finally:
        # Bağlantıyı kapat
        if cur:
            cur.close()

@app.route("/expenses", methods=["GET"])
def expenses():
    """Manage expenses"""

    return render_template("expenses.html")


@login_required
@app.route('/addexpenses', methods=['GET', 'POST'])
def add_expense():
    print("Form Data:", request.form)
    if request.method == 'POST':
        # Formdan gelen verileri al
        amount = request.form["amount"]
        expense_name = request.form["name"]
        category_id = request.form["category"]
        date = request.form["date"]
        description = request.form["description"]


        user_id = session.get('user_id')

        if user_id is None:
            return "Oturum açmış bir kullanıcı bulunamadı."

        try:
            cur = conn.cursor()

            # Harcama eklemek için SQL sorgusu
            insert_query = """
            INSERT INTO expenses (user_id, amount, category_id, date,expense_name, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Sorguya parametreleri ekleyerek harcama ekleme
            cur.execute(insert_query, (user_id, amount, category_id, date,expense_name, description))

            # Değişiklikleri kaydet ve işlemi tamamla
            conn.commit()

            return redirect(url_for('expenses'))

        except psycopg2.Error as e:
            print("Hata:", e)
            return "Harcama eklenirken bir hata oluştu."

        finally:
            # Bağlantıyı kapat
            if cur:
                cur.close()

    else:
        # GET isteği ise, kategorileri al ve harcama ekleme sayfasını render et
        try:
            cur = conn.cursor()

            # Kategorileri veritabanından al
            cur.execute("SELECT id, name FROM categories")
            rows = cur.fetchall()
            categories = [{'id': row[0], 'name': row[1]} for row in rows]

            print("Categories:", categories)  # Kategorileri kontrol et

            """for category in categories:
                print(category.id, category.name)"""

            return render_template('addexpenses.html', categories=categories)

        except psycopg2.Error as e:
            print("Hata:", e)
            return "Kategoriler alınırken bir hata oluştu."

        finally:
            # Bağlantıyı kapat
            if cur:
                cur.close()

@app.route('/expensehistory')
@login_required  # Kullanıcı giriş yapmış olmalı
def expense_history():
    if conn is None:
        return "Veritabanına bağlanırken bir hata oluştu."

    try:
        cur = conn.cursor()

        # Kullanıcının id'sini al
        user_id = session.get('user_id')

        # Kullanıcının harcamalarını veritabanından al
        cur.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
        history = cur.fetchall()

        # HTML sayfasına verileri aktar
        return render_template('expensehistory.html', history=history)

    except psycopg2.Error as e:
        print("Error:", e)
        return "An error occurred while fetching expense history."

    finally:
        # PostgreSQL bağlantısını kapat
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)