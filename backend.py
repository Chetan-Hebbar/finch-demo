from flask import Flask, jsonify, send_from_directory
import os
import base64
import requests
import time

app = Flask(__name__, static_folder=".")

FINCH_CLIENT_ID = "6f7b7625-712a-4963-b2e2-9c7039980a99"
FINCH_CLIENT_SECRET = "finch-secret-sandbox-ZpO9mEz-IODAuhuDBhs5fOnRyiPS6EzQae7NNtAB"
BASE_URL = "https://api.tryfinch.com"

# Store tokens per provider
TOKENS = {}


def create_and_hydrate(provider_id):
    """
    Create a sandbox connection, hydrate data, and return an access token.
    """
    if provider_id in TOKENS:
        return TOKENS[provider_id]

    # Step 1: Create sandbox connection
    auth_token = base64.b64encode(
        f"{FINCH_CLIENT_ID}:{FINCH_CLIENT_SECRET}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {"provider_id": provider_id}

    resp = requests.post(f"{BASE_URL}/sandbox/connections", json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    access_token = data["access_token"]
    time.sleep(5)  # Wait for a moment to ensure the connection is ready

    TOKENS[provider_id] = access_token
    return access_token


@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")


@app.route("/generate/<provider>")
def generate(provider):
    token = create_and_hydrate(provider)
    return jsonify({"status": "ok", "provider": provider})


@app.route("/company/<provider>")
def company_info(provider):
    token = TOKENS.get(provider)
    if not token:
        return jsonify({"error": "No data generated yet. Call /generate first."}), 400

    headers = {"Authorization": f"Bearer {token}", "Finch-API-Version": "2020-09-17"}
    resp = requests.get(f"{BASE_URL}/employer/company", headers=headers)
    resp.raise_for_status()
    return jsonify(resp.json())


@app.route("/employees/<provider>")
def employees(provider):
    token = TOKENS.get(provider)
    if not token:
        return jsonify({"error": "No data generated yet. Call /generate first."}), 400

    headers = {"Authorization": f"Bearer {token}",  "Finch-API-Version": "2020-09-17"}
    resp = requests.get(f"{BASE_URL}/employer/directory", headers=headers)
    resp.raise_for_status()
    return jsonify(resp.json())


if __name__ == "__main__":
    app.run(debug=True)