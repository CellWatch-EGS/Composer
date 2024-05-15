from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
import json
from flask_login import login_required, LoginManager, UserMixin
import requests
import psycopg2
from datetime import datetime
import uuid

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "super secret key"

login_manager = LoginManager()
login_manager.init_app(app)


app.config["SESSION_TYPE"] = "filesystem"
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_SECRET_KEY'] = "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"
app.config['JWT_COOKIE_CSRF_PROJECT'] = False
app.config['JWT_ACCESS_COOKIE_NAME'] = ['access_token']
app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = 'Your_CSRF_Header_Name'
app.config['JWT_ACCESS_CSRF_FIELD_NAME'] = 'Your_CSRF_Field_Name'


DATABASE = "mydb" 
USER = "myuser"
PASSWORD = "123"
HOST = "localhost"

TOKEN = "8ecadf46-9364-4e3a-b79d-182d6a259a75"
headers = {"Authorization": f"Bearer {TOKEN}"}
BASE_URL = "http://127.0.0.1:8000/v1"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    # Aqui você deve implementar a lógica para carregar o usuário do seu banco de dados ou outra fonte de dados
    # Esta função deve retornar uma instância do usuário com o ID fornecido, ou None se o usuário não for encontrado
    return User(user_id)

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
    # login_url = "http://10.139.1.8:5000/login"
    login_url = "http://127.0.0.1:8080/"
    # login_url = "http://127.0.0.1:5000/v1/calendar/1"
    # return redirect(url_for('calendar_page'))

    return redirect(login_url)

@app.route("/v1/create_schedule", methods=["GET"])
def create_schedule():
    eventTime = request.args.get('time')
    eventLocation = request.args.get('locationId')
    eventPerson = request.args.get('person_name')
    calendar_events = []
    
    a = test_create_schedule(eventTime, eventLocation, eventPerson)

    data_parsed = datetime.strptime(a["time"], "%Y-%m-%dT%H:%M:%S")
    data_formatada = data_parsed.strftime("%B/%d/%Y")
    a["time"] = data_formatada

    event_data = {
        "id": a["id"],
        "name": a["locationId"],
        "date": a["time"],
        "description": "Tarde",
        "event": "event",
    }
    calendar_events.append(event_data)
    return redirect(url_for('calendar_page'))

# <int:user_id>
@app.route("/v1/calendar/2", methods=["GET", "POST"])
@login_required
def calendar_page():
    calendar_events = []
    a = test_get_schedules_by_person_name("John Doe")
    print(a)

    for x in a: 
                
        data_parsed = datetime.strptime(x["time"], "%Y-%m-%dT%H:%M:%S")
        data_formatada = data_parsed.strftime("%B/%d/%Y")
        x["time"] = data_formatada

        event_data = {
            "id": x["id"],
            "name": x["locationId"],
            "date": x["time"],
            "description": "Tarde",
            "event": "event",
        }
        calendar_events.append(event_data)

    return render_template("calendar.html", calendar_events=calendar_events)


def test_get_schedules_by_person_name(person_name):
    url = f"{BASE_URL}/schedules/{person_name}"
    response = requests.get(url, headers=headers)
    print("Get Schedule:", response.status_code, response.json())
    assert response.status_code == 200, "Failed to get schedule"
    return response.json()

def test_create_schedule(time, locationId, person_name):
    url = f"http://127.0.0.1:8000/schedules"
    uid = str (uuid.uuid4())
    schedule_data = {
        "id": uid,
        "time": time,
        "locationId": locationId,
        "person_name": person_name
    }
    response = requests.post(url, json=schedule_data, headers=headers)
    assert response.status_code == 201, "Failed to create schedule"
    return response.json()  # Returning the created schedule for further tests

# adicionar description => tipo de shift
# id passar a incrementar automaticamente para n ter q andar sempre a mudar. Se calhar para SERIAL PRIMARY KEY
# def test_create_schedule():
#     url = f"http://127.0.0.1:8000/schedules"
#     # Use a unique identifier for testing, or clean up after tests
#     schedule_data = {
#         "id": "teste1",
#         "time": "2024-04-02T08:00:00",
#         "locationId": "Cozinha",
#         "person_name": "jonas"
#     }
#     response = requests.post(url, json=schedule_data, headers=headers)
#     # print("Create Schedule:", response.status_code, response.json())
#     # print("Create Schedule Response Text:", response.text)
#     assert response.status_code == 201, "Failed to create schedule"
#     return response.json()  # Returning the created schedule for further tests


# Rota para o login
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     user_id = 1
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         print("username:", username)
#         print("password:", password)

#         connection = psycopg2.connect(
#             dbname=DATABASE, user=USER, password=PASSWORD, host=HOST
#         )

#         conn = connection.cursor()

#         query = """SELECT * FROM calendars"""
#         conn.execute(query)
#         users = conn.fetchall()
#         access_token ='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxMjc1NjU5OCwianRpIjoiZjZmMjdjMjctZjc4NC00NDliLTk4ODgtYjQ2MDM2ZjhkNjRiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6NywibmJmIjoxNzEyNzU2NTk4LCJleHAiOjE3MTI3NjAxOTh9.oPoBh9JJqRxjxxvMA-My5oYwBN-3s3kW2vaTKVAz6xU'
#         x = False
#         for row in users:
#             if row[1] == username:
#                 x = True
#                 break

#         if x == True:
#             print("epa n deve ser disto -> "+username)
#             # data = {"email": "user@example.com", "name": username, "password": password}
#             # Endpoint de signup do serviço de autenticação
#             login_url = "http://127.0.0.1:5000/login"
#             headers = {'Authorization': f'Bearer {access_token}'}
#             response = requests.post(login_url, headers=headers)
#             print("hey")
#             if response.status_code == 200:
#                 getinfo_url = "http://127.0.0.1:5000/userinfo"
#                 response = requests.post(getinfo_url, access_token)
#                 return redirect(url_for("calendar_page", user_id=user_id))
#             else:
#                 print("Erro ao fazer login:", response.text)
#                 return render_template("login.html")

#         else:
#             error_message = "Credenciais inválidas. Por favor, tente novamente."
#             return render_template("login.html", error=error_message)

#     return render_template("login.html")


# @app.route("/register")
# def register_page():
#     return render_template("register.html")


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     user_id = 1
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         confirm_password = request.form["confirm_password"]

#         if password != confirm_password:
#             error = "Passwords do not match"
#             return render_template("register.html", error=error)

#         connection = psycopg2.connect(
#             dbname=DATABASE, user=USER, password=PASSWORD, host=HOST
#         )

#         conn = connection.cursor()

#         with open("create_users_table.sql", "r") as file:
#             create_table_query = file.read()
#         conn.execute(create_table_query)

#         query = """SELECT * FROM calendars"""
#         conn.execute(query)
#         users = conn.fetchall()

#         x = False
#         for row in users:
#             if row[1] == username:
#                 x = True
#                 break

#         if x == True:
#             error = "Username already exists"
#             print(error)
#             return render_template("register.html", error=error)
#         else:
#             data = {"email": "user1@example.com", "name": username, "password": password}
#             # Endpoint de signup do serviço de autenticação
#             signup_url = "http://127.0.0.1:5000/signup"

#             # Realizar uma solicitação POST para o endpoint de signup
#             response = requests.post(signup_url, data=data)
#             # if response.status_code == 200:
#             if True:
#                 print("Usuário registrado com sucesso!")
#                 a = test_create_schedule()
#                 postgres_insert_query = """ INSERT INTO calendars (username, password, date, location, shift, type) VALUES (%s,%s,%s,%s,%s,%s)"""
#                 event = "event"
#                 shift = "Noite"
#                 record_to_insert = (
#                     username,
#                     password,
#                     a["time"],
#                     a["locationId"],
#                     shift,
#                     event,
#                 )
#                 conn.execute(postgres_insert_query, record_to_insert)
#                 connection.commit()
#                 count = conn.rowcount
#                 # print(count, "Record inserted successfully into mobile table")
#                 get_vnf_pkgs()
#                 print("deu")
#                 return redirect(url_for("calendar_page"))
#             else:
#                 print("Erro ao registrar usuário:", response.text)
#                 return render_template("register.html")

#         return redirect(url_for("calendar_page", user_id=user_id))

#     return redirect(url_for("calendar_page"), user_id=user_id)


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
    porta = 5000
    # Execute o aplicativo Flask na porta especificada
    app.run(debug=True, port=porta)
