from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
import json
from flask_login import login_required, LoginManager, UserMixin
import requests
import psycopg2
from datetime import datetime
import uuid
# from jwt import ExpiredSignatureError, InvalidTokenError

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "super secret key"

login_manager = LoginManager()
login_manager.init_app(app)

# db.create_all()



# app.config["SESSION_TYPE"] = "filesystem"
# app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JWT_SECRET_KEY'] = "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"
# app.config['JWT_COOKIE_CSRF_PROJECT'] = False
# app.config['JWT_ACCESS_COOKIE_NAME'] = ['access_token']
# app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = 'Your_CSRF_Header_Name'
# app.config['JWT_ACCESS_CSRF_FIELD_NAME'] = 'Your_CSRF_Field_Name'


DATABASE = "mydb" 
USER = "myuser"
PASSWORD = "123"
HOST = "localhost"  

TOKEN = "8ecadf46-9364-4e3a-b79d-182d6a259a75"
headers = {"Authorization": f"Bearer {TOKEN}"}
BASE_URL = "http://127.0.0.1:8000/v1"

users = {}

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Criar um usuário de teste
user = User(id='2', username='b', password='123')
users[user.id] = user

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
@app.route("/composer")
def index():
    # login_url = "http://10.139.1.8:5000/login"
    login_url = "http://127.0.0.1:8082/"
    # login_url = "http://127.0.0.1:5000/v1/calendar/1"
    # return redirect(url_for('calendar_page'))

    return redirect(login_url)

@app.route("/composer/v1/create_schedule", methods=["GET"])
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
@app.route("/composer/v1/calendar/<int:user_id>", methods=["GET", "POST"])
def calendar_page(user_id):
        try:
            user_data = request.cookies.get('user_data')
            if user_data:
                user_data = json.loads(user_data)
                email = user_data.get('email')
                username = user_data.get('username')
                access_token = user_data.get('access_token')
                # Use the email, username, and access token as needed
                # print(f"Email: {email}, Username: {username}, Access Token: {access_token}")
                
            connection = psycopg2.connect(
                dbname=DATABASE, user=USER, password=PASSWORD, host=HOST
            )

            conn = connection.cursor()
            if request.method == "POST":
                data = request.json
                time_str = data.get('time')
                
                # Converter a string de data para o formato datetime
                date_obj = datetime.strptime(time_str, "%d/%m/%Y")
                
                # Formatar a data para o formato desejado com hora fixa de 08:00:00
                formatted_date = date_obj.strftime("%Y-%m-%dT08:00:00")
                print(formatted_date)  # Verificar se a formatação está correta
                
                location = data.get('location')
                shift = data.get('shift')
                
                cursor = connection.cursor()
                postgres_insert_query = """INSERT INTO calendars (username, date, location, shift, type, email) VALUES (%s, %s, %s, %s, %s, %s)"""
                record_to_insert = (username, formatted_date, location, shift, 'event', email)
                
                cursor.execute(postgres_insert_query, record_to_insert)
                connection.commit()
                
                # Chamar as funções necessárias
                test_create_schedule(formatted_date, location, username)
                get_vnf_pkgs(username, email)
                
                # Retornar o template renderizado
                return render_template("calendar.html")

                
            with open("create_users_table.sql", "r") as file:
                create_table_query = file.read()
            conn.execute(create_table_query)

            query = """SELECT * FROM calendars"""
            conn.execute(query)
            users = conn.fetchall()

            x = False
            for row in users:
                if row[1] == username:
                    x = True
                    break

            if x == True:
                calendar_events = []
                
                try:
                    a = test_get_schedules_by_person_name(username)
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
                        print(event_data)
                        calendar_events.append(event_data)
                except Exception as e:
                    print(f"Ocorreu um erro ao tentar obter o valor: {e}")
                
                
            else:
                data = {"email": email, "name": username}
                calendar_events = []
                # a = test_create_schedule()
                postgres_insert_query = """ INSERT INTO calendars (username, date, location, shift, type, email) VALUES (%s,%s,%s,%s,%s, %s)"""
                # event = "event"
                # shift = "Noite"
                # record_to_insert = (
                #     username,
                #     a["time"],
                #     a["locationId"],
                #     shift,
                #     event,
                # )
                record_to_insert = (username, None, None, None, None, email)
                conn.execute(postgres_insert_query, record_to_insert)
                connection.commit()
                count = conn.rowcount
                # print(count, "Record inserted successfully into mobile table")
            return render_template("calendar.html", calendar_events=calendar_events)
        
        except ExpiredSignatureError:
            return "Token has expired", 401
        except InvalidTokenError as e:
            print(f"Invalid token error: {e}")
            return "Invalid token", 401
            
def test_get_schedules_by_person_name(person_name):
    url = f"{BASE_URL}/schedules/{person_name}"
    response = requests.get(url, headers=headers)
    # print("Get Schedule:", response.status_code, response.json())
    assert response.status_code == 200, "Failed to get schedule"
    return response.json()

# @app.route("/v1/calendar/create_schedule", methods=["GET", "POST"])
def test_create_schedule(time, locationId, person_name):
    url = f"{BASE_URL}/schedules/"
    
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

@app.route("/composer/api/v1/vnf_pkgs")
def get_vnf_pkgs(username, email):
    try:
        notification_data = {
            "username": username,
            "email": email,
            "phoneNumber": "+351961799228",
            "systemName": "MySystem",
            "notificationContent": {
                "subject": "Test Notification",
                "body": "Horario adicionado",
            },
            "preferences": {
                "smsEnabled": True,
                "emailEnabled": True,
                "pushEnabled": False,
            },
        }
        response = requests.post(
            "http://127.0.0.1:8005/api/v1/notifications", json=notification_data
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    porta = 5001
    # Execute o aplicativo Flask na porta especificada
    app.run(debug=True, port=porta)
