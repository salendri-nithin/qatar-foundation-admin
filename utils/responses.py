from flask import jsonify
from typing import Any, Optional


def success_response(message: str, data: Any = None, status: int = 200):
    payload = {"status": "success", "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error_response(message: str, status: int = 400):
    return jsonify({"status": "error", "message": message}), status
