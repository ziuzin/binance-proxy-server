from flask import Flask, request, jsonify, Response
import requests
import os
import time
import hmac
import hashlib
from urllib.parse import urlencode

app = Flask(__name__)

# Retrieve Binance API credentials from environment variables
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')

@app.route('/binance_klines')
def binance_klines():
    """
    Proxy public Binance API endpoint /api/v3/klines.
    Expects query parameters like symbol, interval, and limit.
    Returns the JSON response from Binance or an error message.
    """
    params = {k: v for k, v in request.args.items()}
    if 'symbol' not in params or 'interval' not in params:
        return jsonify({'error': 'symbol and interval parameters are required'}), 400
    try:
        response = requests.get('https://api.binance.com/api/v3/klines', params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/binance_account')
def binance_account():
    """
    Make a signed request to Binance /api/v3/account using HMAC SHA256.
    Requires BINANCE_API_KEY and BINANCE_API_SECRET set in environment variables.
    """
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        return jsonify({'error': 'API key and secret must be configured as environment variables'}), 500

    params = {'timestamp': int(time.time() * 1000)}
    for k, v in request.args.items():
        params[k] = v

    query_string = urlencode(params)
    signature = hmac.new(
        BINANCE_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': BINANCE_API_KEY}

    try:
        response = requests.get('https://api.binance.com/api/v3/account', params=params, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# HTML via query string; support both /binance_klines_html and misspelled /binance_klnes_html
@app.route('/binance_klines_html')
@app.route('/binance_klnes_html')
def binance_klines_html():
    """
    HTML representation of the /api/v3/klines response.
    Accepts the same query parameters as /binance_klines.
    Returns an HTML table with kline data.
    """
    params = {k: v for k, v in request.args.items()}
    if 'symbol' not in params or 'interval' not in params:
        return Response('<p>symbol and interval parameters are required</p>', mimetype='text/html'), 400
    try:
        response = requests.get('https://api.binance.com/api/v3/klines', params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return Response(f'<p>Error: {str(e)}</p>', mimetype='text/html'), 500

    headers = [
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
        'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
        'Taker buy quote asset volume', 'Ignore'
    ]
    html = '<table border="1">'
    html += '<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>'
    for row in data:
        html += '<tr>' + ''.join(f'<td>{item}</td>' for item in row) + '</tr>'
    html += '</table>'
    return Response(html, mimetype='text/html')

# HTML via path parameters; support both /binance_klines_html/<...> and misspelled /binance_klnes_html/<...>
@app.route('/binance_klines_html/<symbol>/<interval>/<int:limit>')
@app.route('/binance_klnes_html/<symbol>/<interval>/<int:limit>')
def binance_klines_html_path(symbol, interval, limit):
    """
    HTML representation of the /api/v3/klines response using path parameters.
    Accepts symbol, interval, and limit directly in the URL path.
    Returns an HTML table with kline data.
    """
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    try:
        response = requests.get('https://api.binance.com/api/v3/klines', params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return Response(f'<p>Error: {str(e)}</p>', mimetype='text/html'), 500

    headers = [
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
        'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
        'Taker buy quote asset volume', 'Ignore'
    ]
    html = '<table border="1">'
    html += '<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>'
    for row in data:
        html += '<tr>' + ''.join(f'<td>{item}</td>' for item in row) + '</tr>'
    html += '</table>'
    return Response(html, mimetype='text/html')

# JSON via path parameters; support both /binance_klines/<...> and misspelled /binance_klnes/<...>
@app.route('/binance_klines/<symbol>/<interval>/<int:limit>')
@app.route('/binance_klnes/<symbol>/<interval>/<int:limit>')
def binance_klines_path(symbol, interval, limit):
    """
    Alternative route using path parameters for symbol, interval, and limit.
    Returns the same JSON response as binance_klines.
    """
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    try:
        response = requests.get('https://api.binance.com/api/v3/klines', params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Default to PORT=5000 if not provided by the hosting platform
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
