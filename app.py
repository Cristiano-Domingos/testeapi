import requests
from requests.auth import HTTPBasicAuth
import time
import os
from flask import Flask, jsonify

app = Flask(__name__)

BASE_URL  = os.getenv("PROTHEUS_URL",  "http://tbcsolucoes120800.protheus.cloudtotvs.com.br:4050/rest")
USERNAME  = os.getenv("PROTHEUS_USER", "RPA PROTHEUS")
PASSWORD  = os.getenv("PROTHEUS_PASS", "rpa1234")
TENANT_ID = os.getenv("PROTHEUS_TENANT", "01,")


@app.route("/check")
def check():
    params = {
        "tables":   "SA1",
        "fields":   "A1_COD,A1_NOME",
        "where":    "SA1.D_E_L_E_T_=' '",
        "page":     1,
        "pageSize": 1,
    }
    try:
        t0   = time.monotonic()
        resp = requests.get(
            f"{BASE_URL}/api/framework/v1/genericQuery",
            params=params,
            headers={"tenantid": TENANT_ID},
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=30,
        )
        elapsed = round(time.monotonic() - t0, 2)

        if resp.ok:
            items = resp.json().get("items", [])
            return jsonify({
                "status":   "OK",
                "http":     resp.status_code,
                "tempo_s":  elapsed,
                "registros": items,
            })
        else:
            return jsonify({
                "status":  "FALHA",
                "http":    resp.status_code,
                "erro":    resp.text[:300],
            }), 502

    except requests.exceptions.ConnectionError as e:
        return jsonify({"status": "FALHA", "erro": f"Sem conexao: {e}"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"status": "FALHA", "erro": "Timeout (>30s)"}), 504
    except Exception as e:
        return jsonify({"status": "FALHA", "erro": str(e)}), 500


@app.route("/")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
