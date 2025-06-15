import json
import sqlite3
import os

class Disponibilidade:
    # Caminho absoluto para a base de dados
    current_dir = os.path.dirname(os.path.abspath(__file__))
    userlogin_dir = os.path.dirname(current_dir)
    path = os.path.join(userlogin_dir, 'data', 'disponibilidade.db')

    @classmethod
    def get_disponibilidades(cls, user_id):
        """Lê as disponibilidades do utilizador da coluna disponibilidades (JSON)"""
        con = sqlite3.connect(cls.path)
        cur = con.cursor()
        cur.execute("SELECT disponibilidades FROM Userlogin WHERE id=?", (user_id,))
        result = cur.fetchone()
        con.close()
        if result and result[0] is not None and str(result[0]).strip() not in ("", "null"):
            try:
                return json.loads(result[0])
            except Exception:
                return []
        return []

    @classmethod
    def set_disponibilidades(cls, user_id, disponibilidades):
        """Guarda as disponibilidades (lista/dict) como JSON na coluna disponibilidades"""
        disponibilidades_json = json.dumps(disponibilidades)
        con = sqlite3.connect(cls.path)
        cur = con.cursor()
        cur.execute("UPDATE Userlogin SET disponibilidades=? WHERE id=?", (disponibilidades_json, user_id))
        con.commit()
        con.close()

    @classmethod
    def set_bloqueio(cls, date, bloquear):
        """Guarda o bloqueio de um dia (exemplo simples em ficheiro JSON)"""
        bloqueio_path = os.path.join(cls.userlogin_dir, 'data', 'bloqueios.json')
        # Lê bloqueios existentes
        if os.path.exists(bloqueio_path):
            with open(bloqueio_path, 'r', encoding='utf-8') as f:
                bloqueios = json.load(f)
        else:
            bloqueios = {}

        if bloquear:
            bloqueios[date] = True
        else:
            bloqueios.pop(date, None)

        with open(bloqueio_path, 'w', encoding='utf-8') as f:
            json.dump(bloqueios, f, ensure_ascii=False, indent=2)

    @classmethod
    def is_bloqueado(cls, date):
        """Verifica se um dia está bloqueado"""
        bloqueio_path = os.path.join(cls.userlogin_dir, 'data', 'bloqueios.json')
        if os.path.exists(bloqueio_path):
            with open(bloqueio_path, 'r', encoding='utf-8') as f:
                bloqueios = json.load(f)
            return bloqueios.get(date, False)
        return False