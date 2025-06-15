import bcrypt
password = "FRAC"  # Substitua pela password desejada
hash_ = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hash_.decode())