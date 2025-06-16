import sys, os
from flask import render_template, request, session, redirect
from classes.disponibilidade import Disponibilidade
from classes.userlogin import Userlogin
import calendar
from datetime import date

current_dir = os.path.dirname(os.path.abspath(__file__))
userlogin_dir = os.path.dirname(current_dir)
classes = os.path.join(userlogin_dir, 'classes')
sys.path.append(classes)

from .datafile import filename

prev_option = ""
Userlogin.read(filename)

def generate_calendar():
    """Gera um calendário com os dias de julho a setembro, alinhando o 1º dia da semana"""
    calendar_data = {}
    for month in range(7, 10):  # Meses de julho (7) a setembro (9)
        days = []
        first_weekday, num_days = calendar.monthrange(2025, month)
        # Ajuste para segunda-feira como primeiro dia (Python: segunda=0)
        for _ in range((first_weekday - 0) % 7):
            days.append(None)
        for day in range(1, num_days + 1):
            days.append({
                "date": date(2025, month, day).strftime("%Y-%m-%d"),
                "day": day,
                "status": "sim"  # Default é "sim"
            })
        calendar_data[month] = days
    return calendar_data

def index():
    user = session.get("user")
    if not user:
        return redirect("/login")
    user_id = Userlogin.get_user_id(user)

    # Lê as disponibilidades do utilizador
    disponibilidades = Disponibilidade.get_disponibilidades(user_id)

    # Gera o calendário
    calendar_data = generate_calendar()

    # Atualiza o calendário com as disponibilidades existentes
    for month, days in calendar_data.items():
        for day in days:
            if day is None:
                continue
            for disponibilidade in disponibilidades:
                if day["date"] == disponibilidade["data"]:
                    day["status"] = disponibilidade["status"]

    return render_template(
        "disponibilidade.html",
        calendar=calendar_data,  # Passa o calendário para o template
        ulogin=user
    )