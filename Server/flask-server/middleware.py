from flask import request, abort, current_app
from config import ALLOWED_IPS

def ip_restriction():
    if current_app.config.get("TESTING"):
        return  # Ignora IP check nos testes

    if request.remote_addr not in ALLOWED_IPS:
        abort(403)
