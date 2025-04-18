import os
from flask import Flask, render_template, redirect, jsonify
import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

API_KEY = '0Q1V8UQTYXP825ZW'
GOLD_URL = 'https://www.alphavantage.co/query'

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'frontend'),
            static_folder=os.path.join(BASE_DIR, 'frontend', 'static'))

@app.route("/")
def home():
    #if request.host.startswith("www."):
    #    return redirect("https://lacentraldeloro.com", code=301)
    return render_template("index.html")

@app.route('/compro_oro_plata')
def compro_oro_y_plata():
    return render_template('compro_oro_plata.html')

@app.route('/casa_empenos')
def casa_empeños():
    return render_template('casa_empenos.html')

@app.route('/oro_inversion')
def oro_inversion():
    return render_template('oro_inversion.html')


@app.route('/gold-data')
def gold_data():
    # Paso 1: Obtener el histórico de precios XAU/USD
    params = {
        'function': 'TIME_SERIES_MONTHLY',
        'symbol': 'XAUUSD',
        'apikey': API_KEY
    }
    response = requests.get(GOLD_URL, params=params)
    data = response.json()

    if 'Monthly Time Series' not in data:
        return jsonify({'error': 'No se pudieron obtener datos'}), 500

    time_series = data['Monthly Time Series']
    sorted_dates = sorted(time_series.keys(), reverse=True)[:60]  # Últimos 60 meses

    # Paso 2: Obtener el tipo de cambio USD → EUR (solo una vez)
    fx_params = {
        'function': 'CURRENCY_EXCHANGE_RATE',
        'from_currency': 'USD',
        'to_currency': 'EUR',
        'apikey': API_KEY
    }
    fx_response = requests.get("https://www.alphavantage.co/query", params=fx_params)
    fx_data = fx_response.json()

    if "Realtime Currency Exchange Rate" not in fx_data:
        return jsonify({'error': 'No se pudo obtener el tipo de cambio'}), 500

    usd_to_eur = float(fx_data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])

    # Paso 3: Calcular EUR/gramo por cada mes
    history = []
    for date in sorted(sorted_dates):  # cronológicamente
        usd_per_oz = float(time_series[date]['4. close'])
        eur_per_gram = (usd_per_oz * usd_to_eur) / 31.1035
        history.append({
            'date': date,
            'eur_per_gram': round(eur_per_gram, 2)
        })

    return jsonify(history)

@app.route('/venta_joyas')
def venta_joyas():
    return render_template('venta_joyas.html')

if __name__ == "__main__":
    app.run(debug=True)


# compro oro. collar principal, anillos, efectivo, apreton de manos sin pistolas
# empeños. reloj fondo. taller, calendario, caja fuerte
# oro inversion. bolsa, oro
# venta joyas. escaparate joyas, chica joya, caja joyas