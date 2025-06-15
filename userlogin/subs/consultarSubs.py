import sys, os
from flask import render_template, request, session, redirect, jsonify
from classes.userlogin import Userlogin
from classes.disponibilidade import Disponibilidade
import calendar
from datetime import date

def generate_calendar():
    """Gera um calendário de julho a setembro de 2025"""
    calendar_data = {}
    for month in range(7, 10):
        days = []
        num_days = calendar.monthrange(2025, month)[1]
        for day in range(1, num_days + 1):
            date_str = date(2025, month, day).strftime("%Y-%m-%d")
            days.append({
                "date": date_str,
                "day": day,
                "users": [],
                "bloqueado": Disponibilidade.is_bloqueado(date_str)
            })
        calendar_data[month] = days
    return calendar_data

def geral():
    user = session.get("user")
    if not user:
        return redirect("/login")
    user_id = Userlogin.get_user_id(user)
    group = Userlogin.obj[user_id].usergroup if user_id in Userlogin.obj else "user"

    # Obter todos os utilizadores
    all_users = list(Userlogin.obj.values())

    # Obter filtro de status do GET ou usar default
    status_filter = request.args.getlist("status")
    if not status_filter:
        status_filter = ["talvez", "não"]  # Por default não mostra "sim"

    # Gera o calendário
    calendar_data = generate_calendar()

    # Preenche o calendário com os nomes e status de cada utilizador
    for u in all_users:
        disponibilidades = Disponibilidade.get_disponibilidades(u.id)
        for disponibilidade in disponibilidades:
            d = disponibilidade["data"]
            s = disponibilidade["status"]
            # Encontrar o mês e o dia
            dt = date.fromisoformat(d)
            if dt.month in calendar_data:
                for day in calendar_data[dt.month]:
                    if day["date"] == d:
                        day["users"].append({
                            "name": u.user,
                            "status": s
                        })

    return render_template(
        "consultar.html",
        calendar=calendar_data,
        status_filter=status_filter,
        ulogin=user,
        group=group
    )