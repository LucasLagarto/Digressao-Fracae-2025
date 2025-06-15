import os

# Caminho absoluto do diretório atual (subs)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho para a pasta 'userlogin' (um nível acima de subs)
userlogin_dir = os.path.dirname(current_dir)

# Caminho para a base de dados
filename = (userlogin_dir+'/data'+'/disponibilidade.db')
print(filename)