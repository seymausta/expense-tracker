import psycopg2
from flask import Flask, render_template, redirect, request, session, url_for
from init_db import get_database_connection, close_database_connection
from helpers import login_required
#from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.secret_key = "your_secret_key"
#csrf = CSRFProtect(app)

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

        conn = get_database_connection()

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
            close_database_connection(conn)

    return redirect("/login", 302)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        # Formdan gelen verileri al
        email = request.form["email"]
        password = request.form["password"]

        conn = get_database_connection()

        try:
            cur = conn.cursor()

            # Kullanıcıyı veritabanında sorgula
            cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cur.fetchone()

            if user:
                # Kullanıcı varsa oturumu başlat
                session['logged_in'] = True
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
            close_database_connection(conn)

@app.route("/logout")
def logout():
    # Oturumu sonlandır
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect("/",302)

@app.route('/account')
def account():
    conn = get_database_connection()
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
        close_database_connection(conn)

@app.route("/expenses", methods=["GET"])
def expenses():
    """Manage expenses"""

    return render_template("expenses.html")

@login_required
@app.route('/addexpenses', methods=['GET', 'POST'])
def add_expense():
    conn = get_database_connection()
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
            close_database_connection(conn)

    else:
        # GET isteği ise, kategorileri al ve harcama ekleme sayfasını render et
        try:
            cur = conn.cursor()

            # Kategorileri veritabanından al
            cur.execute("SELECT id, name FROM categories")
            rows = cur.fetchall()
            categories = [{'id': row[0], 'name': row[1]} for row in rows]

            print("Categories:", categories)  # Kategorileri kontrol et

            return render_template('addexpenses.html', categories=categories)

        except psycopg2.Error as e:
            print("Hata:", e)
            return "Kategoriler alınırken bir hata oluştu."

        finally:
            # Bağlantıyı kapat
            if cur:
                cur.close()
            close_database_connection(conn)

@app.route('/expensehistory')
@login_required  # Kullanıcı giriş yapmış olmalı
def expense_history():
    conn = get_database_connection()  # Veritabanı bağlantısını al
    if conn is None:
        return "Veritabanına bağlanırken bir hata oluştu."

    try:
        cur = conn.cursor()

        # Kullanıcının id'sini al
        user_id = session.get('user_id')

        # Kullanıcının harcamalarını veritabanından sadece belirli sütunları alarak al
        cur.execute("SELECT expense_name, amount, date, description, category_id,id FROM expenses WHERE user_id = %s", (user_id,))
        expenses = cur.fetchall()

        # Her bir harcama için kategori adını al ve yeni bir liste oluştur
        history = []
        for expense in expenses:
            expense_name, amount, date, description, category_id,id = expense
            cur.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
            category_name = cur.fetchone()[0]  # Kategori adını al
            history.append((expense_name, amount, date, description, category_name,id))

        # HTML sayfasına verileri aktar
        return render_template('expensehistory.html', history=history)

    except psycopg2.Error as e:
        print("Error:", e)
        return "An error occurred while fetching expense history."

    finally:
        # PostgreSQL bağlantısını kapat
        if conn:
            conn.close()

@app.route('/deleteexpense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    conn = get_database_connection()
    if conn is None:
        return "Veritabanına bağlanırken bir hata oluştu."

    try:
        cur = conn.cursor()

        # Kullanıcının giriş yapmış olduğunu kontrol et
        user_id = session.get('user_id')
        if user_id is None:
            return "Oturum açmış bir kullanıcı bulunamadı."

        # Kullanıcının belirtilen harcamayı silebilmesi için gerekli yetkilere sahip olduğunu kontrol et
        cur.execute("SELECT user_id FROM expenses WHERE id = %s", (expense_id,))
        result = cur.fetchone()

        if result is not None and result[0] == user_id:
            # Belirtilen harcamayı sil
            cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
            conn.commit()
            return redirect(url_for('expense_history'))
        else:
            return "Bu harcamayı silme izniniz yok."

        # Belirtilen harcamayı sil
        cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()

        return redirect(url_for('expense_history'))

    except psycopg2.Error as e:
        print("Hata:", e)
        return "Harcama silinirken bir hata oluştu."

    finally:
        # Bağlantıyı kapat
        if conn:
            conn.close()


@app.route('/updateexpense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def update_expense(expense_id):
    conn = get_database_connection()
    if request.method == 'POST':
        if conn is None:
            return "Veritabanına bağlanırken bir hata oluştu."

        try:
            cur = conn.cursor()

            # Kullanıcının giriş yapmış olduğunu kontrol et
            user_id = session.get('user_id')
            if user_id is None:
                return "Oturum açmış bir kullanıcı bulunamadı."

            # Kullanıcının belirtilen harcamayı güncelleyebilmesi için gerekli yetkilere sahip olduğunu kontrol et
            cur.execute("SELECT user_id FROM expenses WHERE id = %s", (expense_id,))
            result = cur.fetchone()
            if not result or result[0] != user_id:
                return "Bu harcamayı güncelleme izniniz yok."

            # Requestten form verilerine erişin
            new_name = request.form["newName"]
            new_amount = request.form["newAmount"]
            new_category = request.form["newCategory"]
            new_date = request.form["newDate"]
            new_description = request.form["newDescription"]

            # Harcamayı güncelle
            cur.execute(
                "UPDATE expenses SET expense_name = %s, amount = %s, category_id = %s, date = %s, description = %s WHERE id = %s",
                (new_name, new_amount, new_category, new_date, new_description, expense_id))
            conn.commit()

            return redirect(url_for('expensehistory'))

        except psycopg2.Error as e:
            print("Hata:", e)
            return "Harcama güncellenirken bir hata oluştu."

        finally:
            # Bağlantıyı kapat
            if conn:
                conn.close()
    else:
        # GET isteği ise, kategorileri al ve harcama ekleme sayfasını render et
        try:
            cur = conn.cursor()

            # Kategorileri veritabanından al
            cur.execute("SELECT id, name FROM categories")
            rows = cur.fetchall()
            categories = [{'id': row[0], 'name': row[1]} for row in rows]

            print("Categories:", categories)  # Kategorileri kontrol et

            return render_template('expensehistory.html', categories=categories)

        except psycopg2.Error as e:
            print("Hata:", e)
            return "Kategoriler alınırken bir hata oluştu."

        finally:
            # Bağlantıyı kapat
            if cur:
                cur.close()
            close_database_connection(conn)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
