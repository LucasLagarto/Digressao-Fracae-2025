import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, session, redirect, jsonify
from classes.userlogin import Userlogin
from classes.disponibilidade import Disponibilidade
from subs import disponibilidadeSubs
from subs import userloginSubs
from subs import consultarSubs
from subs import excelSubs  # Adicione esta linha junto com os outros imports de subs
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:  # Verifica se o usuário está logado
            return redirect("/login")  # Redireciona para a página de login
        return f(*args, **kwargs)
    return decorated_function

@app.route("/disponibilidade", methods=["POST", "GET"])
@login_required
def disponibilidade():
    return disponibilidadeSubs.index()

@app.route('/update_status', methods=['POST'])
def update_status():
    try:
        data = request.get_json()
        print(f"Dados recebidos: {data}")  # Log para depuração

        date = data.get('date')
        status = data.get('status')
        user_id = session.get("user_id")

        print(f"user_id: {user_id}, date: {date}, status: {status}")  # Log para depuração

        if not user_id or not date or not status:
            return jsonify({"error": "Dados inválidos"}), 400

        # Lê as disponibilidades atuais
        disponibilidades = Disponibilidade.get_disponibilidades(user_id)

        # Atualiza ou adiciona a disponibilidade
        updated = False
        for disponibilidade in disponibilidades:
            if disponibilidade["data"] == date:
                disponibilidade["status"] = status
                updated = True
                break
        if not updated:
            disponibilidades.append({"data": date, "status": status})

        # Guarda as disponibilidades atualizadas
        Disponibilidade.set_disponibilidades(user_id, disponibilidades)

        return jsonify({"success": True})
    except Exception as e:
        print(f"Erro ao atualizar disponibilidade: {e}")
        return jsonify({"error": "Erro interno no servidor"}), 500

@app.route("/")
def index():
    return render_template("index.html", ulogin=session.get("user"))

@app.route("/login")
def login():
    return render_template("login.html", id=0, user="", password="", ulogin=session.get("user"), resul="")

@app.route("/logoff")
def logoff():
    session.pop("user", None)
    session.pop("user_id", None)  # Remove também o user_id da sessão
    return redirect("/")

@app.route("/chklogin", methods=["POST", "GET"])
def chklogin():
    user = request.form["user"]
    password = request.form["password"]
    resul = Userlogin.chk_password(user, password)
    if resul == "Valid":
        session["user"] = user
        session["user_id"] = Userlogin.user_id  # Corrige o uso de user_id

        # Preencher disponibilidades se for a primeira vez (null ou vazio)
        user_id = Userlogin.user_id
        disponibilidades = Disponibilidade.get_disponibilidades(user_id)
        if not disponibilidades:  # Se for None ou lista vazia
            # Gerar todas as datas de julho a setembro como "sim"
            import calendar
            from datetime import date
            novas_disponibilidades = []
            for month in range(7, 10):
                num_days = calendar.monthrange(2025, month)[1]
                for day in range(1, num_days + 1):
                    novas_disponibilidades.append({
                        "data": date(2025, month, day).strftime("%Y-%m-%d"),
                        "status": "sim"
                    })
            Disponibilidade.set_disponibilidades(user_id, novas_disponibilidades)

        return redirect("/")
    return render_template("login.html", user=user, password=password, ulogin=session.get("user"), resul=resul)

@app.route("/Userlogin", methods=["POST", "GET"])
@login_required
def userlogin():
    return userloginSubs.userlogin()

@app.route("/consultar", methods=["GET"])
def geral():
    return consultarSubs.geral()

@app.route("/excel")
def excel():
    return excelSubs.index()

# Para admin alterar status de qualquer user
@app.route('/update_status_admin', methods=['POST'])
def update_status_admin():
    from classes.userlogin import Userlogin
    from classes.disponibilidade import Disponibilidade
    data = request.get_json()
    user = data.get('user')
    date_ = data.get('date')
    status = data.get('status')
    user_id = Userlogin.get_user_id(user)
    if not user_id or not date_ or not status:
        return jsonify({"error": "Dados inválidos"}), 400
    disponibilidades = Disponibilidade.get_disponibilidades(user_id)
    updated = False
    for disponibilidade in disponibilidades:
        if disponibilidade["data"] == date_:
            disponibilidade["status"] = status
            updated = True
            break
    if not updated:
        disponibilidades.append({"data": date_, "status": status})
    Disponibilidade.set_disponibilidades(user_id, disponibilidades)
    return jsonify({"success": True})

@app.route('/bloquear_dia', methods=['POST'])
def bloquear_dia():
    from classes.disponibilidade import Disponibilidade
    data = request.get_json()
    date_ = data.get('date')
    bloquear = data.get('bloquear')
    # Aqui deve guardar o bloqueio (ex: ficheiro json, db, etc)
    Disponibilidade.set_bloqueio(date_, bloquear)
    return jsonify({"success": True})

# COMENTAR ISTO ANTES DE CORRER NO PYTHONANYWHERE
if __name__ == '__main__':
    app.run(debug=True)