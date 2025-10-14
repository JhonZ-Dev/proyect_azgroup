# app/utils/sign_link.py
import hmac, hashlib, time
from typing import Optional

def sign_token(secret: str, payload: str, ttl_seconds: int = 3600) -> str:
    exp = int(time.time()) + ttl_seconds
    data = f"{payload}.{exp}"
    sig = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{exp}.{sig}"

def verify_token(secret: str, token: str, expected_payload: str) -> bool:
    try:
        payload, exp_s, sig = token.rsplit(".", 2)
        if payload != expected_payload:
            return False
        exp = int(exp_s)
        if time.time() > exp:
            return False
        data = f"{payload}.{exp}"
        sig_calc = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig_calc, sig)
    except Exception:
        return False
