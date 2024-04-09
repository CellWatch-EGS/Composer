from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import requests
import psycopg2


app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"


DATABASE = "mydb"
USER = "myuser"
PASSWORD = "123"
HOST = "localhost"


def connect_db():
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cur = conn.cursor()
    # Ler e executar o arquivo SQL
    with open("create_users_table.sql", "r") as f:
        create_table_query = f.read()
    cur.execute(create_table_query)
    conn.commit()
    return conn


# Rota para a página inicial
@app.route("/")
def index():
    return redirect(url_for("calendar_page"))
# <int:user_id>
@app.route("/v1/calendar/user_id")
def calendar_page():
    # Estabelece a conexão com o banco de dados
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cursor = conn.cursor()

    # Executa a consulta para obter os eventos da base de dados
    cursor.execute("SELECT id, name, date, description, type FROM calendars")

    # Recupera os resultados da consulta
    events_from_db = cursor.fetchall()

    # Formata os eventos para o formato necessário pelo plugin do calendário
    calendar_events = []
    for event in events_from_db:
        print(event)
        event_data = {
            "id": event[0],
            "name": event[1],
            "date": event[2],
            "description": event[3],
            "type": event[4],
        }
        calendar_events.append(event_data)

    # Renderiza o template HTML e passa os eventos como um argumento
    return render_template("calendar.html", calendar_events=calendar_events)
    


# Rota para o login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print("username:", username)
        print("password:", password)

        conn = psycopg2.connect(
            dbname=DATABASE, user=USER, password=PASSWORD, host=HOST
        )
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        print("user:", user)

        if user is not None and password == user[1]:
            user_id = user[0]
            return redirect(url_for("welcome", user_id=user_id))

        error_message = "Credenciais inválidas. Por favor, tente novamente."
        return render_template("login.html", error=error_message)

    return render_template("login.html")


@app.route("/v1/schedule/<int:user_id>")
def welcome(user_id):
    # Consulta ao banco de dados para recuperar os horários do usuário
    user_schedule = get_user_schedule(user_id)
    schedule_json = json.dumps(user_schedule)
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return render_template(
        "welcome.html", username=user[0], schedule_json=schedule_json
    )


def get_user_schedule(user_id):
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    c = conn.cursor()
    c.execute("SELECT * FROM schedule WHERE id=?", (user_id,))
    user_schedule = c.fetchall()
    conn.close()
    return user_schedule


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            error = "Passwords do not match"
            return render_template("register.html", error=error)

        connection = psycopg2.connect(
            dbname=DATABASE, user=USER, password=PASSWORD, host=HOST
        )

        conn = connection.cursor()

        with open("create_users_table.sql", "r") as file:
            create_table_query = file.read()
        conn.execute(create_table_query)

        query = """SELECT * FROM users"""
        conn.execute(query)
        print("Selecting rows from mobile table using cursor.fetchall")
        users = conn.fetchall()

        print("Print each row and it's columns values")
        x = False
        for row in users:
            if row[1] == username:
                x = True
                break
        print(x)

        if x == True:
            error = "Username already exists"
            print(error)
            return render_template("register.html", error=error)
        else:
            postgres_insert_query = (
                """ INSERT INTO users (username, password) VALUES (%s,%s)"""
            )
            record_to_insert = (username, password)
            conn.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            count = conn.rowcount
            print(count, "Record inserted successfully into mobile table")
            get_vnf_pkgs()

            # alterar isto para fazer o insert na outra bd (ainda n esta criada)
            # alem disso tirar o render (linha 157) e deixar o redirect

            # password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            # c.execute("SELECT id FROM users WHERE username=?", (username,))
            # user_id = c.lastrowid
            # c.execute(
            #     "INSERT INTO schedule (id, guardID, time, locationID) VALUES (?, ?, ?, ?)",
            #     (user_id, f"guard_{user_id}", "2002-01-10", "Dormir"),
            # )
        return render_template("register.html")

        # return redirect(url_for("welcome", user_id=0))

    return render_template("register.html")


@app.route("/api/v1/vnf_pkgs")
def get_vnf_pkgs():
    try:
        notification_data = {
            "username": "john_doe",
            "email": "jprferreira2002@gmail.com",
            "phoneNumber": "+351961799228",
            "systemName": "MySystem",
            "notificationContent": {
                "subject": "Test Notification",
                "body": "This is a test notification.",
            },
            "preferences": {
                "smsEnabled": False,
                "emailEnabled": False,
                "pushEnabled": False,
            },
        }
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/notifications", json=notification_data
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
