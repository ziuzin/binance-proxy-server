from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/binance_klines')
def binance_klines():
    base_url = "https://api.binance.com/api/v3/klines"
    raw_params = {
        "symbol": request.args.get("symbol"),
        "interval": request.args.get("interval"),
        "startTime": request.args.get("startTime"),
        "endTime": request.args.get("endTime"),
        "limit": request.args.get("limit"),
    }
    params = {k: v for k, v in raw_params.items() if v}
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        print(f"[binance_proxy] Status: {resp.status_code}")
        print(f"[binance_proxy] Body: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        return jsonify(data)
    except requests.HTTPError as e:
        return jsonify({
            "error": "Upstream error",
            "status_code": e.response.status_code,
            "detail": e.response.text
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Unexpected error",
            "detail": str(e)
        }), 500

@app.route('/binance_klines_html')
def binance_klines_html():
    base_url = "https://api.binance.com/api/v3/klines"
    raw_params = {
        "symbol": request.args.get("symbol"),
        "interval": request.args.get("interval"),
        "startTime": request.args.get("startTime"),
        "endTime": request.args.get("endTime"),
        "limit": request.args.get("limit"),
    }
    params = {k: v for k, v in raw_params.items() if v}
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        print(f"[binance_proxy_html] Status: {resp.status_code}")
        print(f"[binance_proxy_html] Body: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        pretty_json = json.dumps(data, indent=2)
        return f"<html><body><h1>Binance Klines</h1><pre>{pretty_json}</pre></body></html>"
    except Exception as e:
        return f"<html><body><pre>Error: {str(e)}</pre></body></html>", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
