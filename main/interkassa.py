import base64
from hashlib import sha256

def interkassa_sign_check(post, secret):  #функция проверки сигны
    data = []
    for x in sorted(post.keys()):
        if x.startswith('ik_') and x != 'ik_sign':
            data.append(str(post.get(x)))
    data.append(secret)
    sign = base64.b64encode(sha256(":".join(data).encode()).digest()).decode()
    print(sign)
    if 'ik_sign' in post.keys() and sign == post.get('ik_sign'):
        return True
    else:
        return False