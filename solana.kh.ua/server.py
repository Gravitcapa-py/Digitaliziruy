import base64
import hmac
import hashlib
import json
from typing import Optional
from fastapi import FastAPI, Form, Cookie, Body
from fastapi.responses import Response

app = FastAPI()

SECRET_KEY = "bd72dc5be81c4d2309a0c568982f12bc7f12a90f07d4186d45c55248fccfa46d"
PASSWORD_SALT = "0fe7c96577f8c6b0f9eba12e37f408b2ed339886604165d9a0d888d6a465c41d"


def sign_data(data: str) -> str:
    """Return signed data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()


def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
    return password_hash == stored_password_hash


users = {
    "alexey@user.com": {
        "name": "Alexey",
        "password": "bf5173b585fddba2c95fcdce17390fab7fddd1ed8c90760ea73f0fb5f4d3a9b6",
        "balance": 100_000
    },
    "petr@user.com": {
        "name": "Petr",
        "password": "99d32de2daa498fdd83cfde91ada52b22e8b34c13ae1dfbd30723a86adbb3cbf",
        "balance": 555_555
    }
}


@app.get("/")
def index_page(username: Optional[str] = Cookie(default=None)):
    with open("templates/login.html", "r") as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    return Response(
        f"Hello, {users[valid_username]['name']}!<br />"
        f"Balance, {users[valid_username]['balance']}!",
        media_type="text/html")


@app.post("/login")
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                "success": False,
                "message": "I don't know you!"
            }),
            media_type="application/json")

    response = Response(
        json.dumps({
            "success": True,
            "message": f"Hello, {user['name']}!<br /> Balance: {user['balance']}"
        }),
        media_type='application/json')
    username_signed = base64.b64encode(username.encode()).decode() + "." + sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response
