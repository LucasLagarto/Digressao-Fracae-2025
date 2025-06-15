import bcrypt
import sqlite3
import json
import os
# Import the generic class
from classes.gclass import Gclass

class Userlogin(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # class attributes, identifier attribute '_id' must be the first one on the list
    att = ['_id', '_user', '_usergroup', '_password', '_disponibilidades']
    # Class header title
    header = 'Userlogin'
    # field description for use in, for example, in input form
    des = ['Id', 'User', 'Usergroup', 'Password', 'Disponibilidades']
    username = ''
    user_id = 0
    # Constructor: Called when an object is instantiated
    def __init__(self, id, user, usergroup, password, disponibilidades=None):
        super().__init__()
        # Object attributes
        id = Userlogin.get_id(id)
        self._id = id
        self._user = user
        self._usergroup = usergroup
        self._password = password
        self._disponibilidades = disponibilidades
        # Add the new object to the dictionary of objects
        Userlogin.obj[id] = self
        # Add the code to the list of object codes
        Userlogin.lst.append(id)
    # id property getter method
    @property
    def id(self):
        return self._id
    # user property getter method
    @property
    def user(self):
        return self._user
    # usergroup property getter method
    @property
    def usergroup(self):
        return self._usergroup
    @usergroup.setter
    def usergroup(self, usergroup):
        self._usergroup = usergroup
    # password property
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, password):
        self._password = password

    @classmethod
    def get_user_id(cls, user):
        user_id = 0
        lsobj = Userlogin.find(user, 'user')
        if len(lsobj) == 1:
            obj = lsobj[0]
            user_id = obj.id
        return user_id            
    @classmethod
    def chk_password(cls, user, password):
        Userlogin.username = ''
        user_id = Userlogin.get_user_id(user)
        if user_id != 0:
            obj = Userlogin.obj[user_id]
            hash_ = obj._password
            # Check if hash looks like bcrypt
            if not (isinstance(hash_, str) and hash_.startswith("$2")):
                return 'Password hash invalid (not bcrypt)'
            try:
                valid = bcrypt.checkpw(password.encode(), hash_.encode())
            except ValueError:
                return 'Password hash invalid (corrupted)'
            if valid:
                Userlogin.user_id = obj.id
                Userlogin.username = obj.user
                message = "Valid"
            else:
                message = 'Wrong password'
        else:
            message = 'No existent user'
        return message
    @classmethod
    def set_password(cls, password):
        passencrypted = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return passencrypted.decode()
    
    def __str__(self):
        return f'Id:{self.id}, User:{self.user}, Usergroup:{self.usergroup}'

    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'disponibilidade.db')

    @classmethod
    def insert(cls, obj):
        print("A INSERIR NA DB")
        conn = sqlite3.connect(cls.db_path)
        cur = conn.cursor()
        disponibilidades_json = json.dumps(getattr(obj, 'disponibilidades', getattr(obj, '_disponibilidades', [])))
        cur.execute(
            "INSERT INTO Userlogin (user, usergroup, password, disponibilidades) VALUES (?, ?, ?, ?)",
            (obj.user, obj.usergroup, obj.password, disponibilidades_json)
        )
        conn.commit()
        obj._id = cur.lastrowid
        conn.close()
        return obj._id
    @classmethod
    def update_custom(cls, obj, update_disponibilidades=False):
        """
        Atualiza o utilizador na base de dados.
        Se update_disponibilidades=False, mantém o valor atual de disponibilidades na base de dados.
        Se update_disponibilidades=True, atualiza disponibilidades com o valor do objeto.
        """
        conn = sqlite3.connect(cls.db_path)
        cur = conn.cursor()

        if update_disponibilidades:
            disponibilidades_json = json.dumps(getattr(obj, '_disponibilidades', []))
            cur.execute(
                "UPDATE Userlogin SET user=?, usergroup=?, password=?, disponibilidades=? WHERE id=?",
                (obj.user, obj.usergroup, obj.password, disponibilidades_json, obj.id)
            )
        else:
            # Mantém o valor atual de disponibilidades na base de dados
            cur.execute(
                "UPDATE Userlogin SET user=?, usergroup=?, password=? WHERE id=?",
                (obj.user, obj.usergroup, obj.password, obj.id)
            )

        conn.commit()
        conn.close()