print("Hello World!")
import time
import hashlib
import hmac
import base64

base_url = 'https://api.switch-bot.com'

token = "5633784875c5d2a2efd67c6659ecf3c04a707d38d69128f021129bc9dc329e09f9625169d0b74e1d04bc838f04806079"
secret = "e49e2ac4b4aa8f88f297d6c0e80fffa6"

def make_request_header(token: str,secret: str) -> dict:
    nonce = ''
    t = int(round(time.time() * 1000))
    string_to_sign = bytes(f'{token}{t}{nonce}', 'utf-8')
    secret = bytes(secret, 'utf-8')
    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
    
    headers={
            "Authorization": token,
            "sign": sign,
            "t": str(t),
            "nonce": nonce
        }
    return headers
