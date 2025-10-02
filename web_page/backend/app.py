import os
import requests
from flask import flash, Flask, render_template, redirect, jsonify, request, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, event

ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS = os.environ.get("ADMIN_PASS")

print("DEBUG → ADMIN_USER:", ADMIN_USER)
print("DEBUG → ADMIN_PASS:", ADMIN_PASS)

API_KEY = '0Q1V8UQTYXP825ZW'
GOLD_URL = 'https://www.alphavantage.co/query'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:OLoVstzDuNTjWNnNPgAKXCtkXpcVrLdP@postgres.railway.internal:5432/railway'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

# Modelo
class Joya(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(50), nullable=False)
    diamante = db.Column(db.Boolean, default=False)
    precio = db.Column(db.Numeric(10,2), nullable=False)
    descripcion = db.Column(db.Text)
    foto = db.Column(db.Text)

@event.listens_for(Joya, "before_insert")
def generar_id(mapper, connection, target):
    prefix = target.material[:2].lower() + target.tipo[:2].lower()
    if target.diamante:
        prefix += "d"
    result = connection.execute(text("SELECT nextval('joya_seq')"))
    counter = str(result.fetchone()[0]).zfill(3)
    target.id = prefix + counter

# 🔹 Crear tablas y secuencia al arrancar
with app.app_context():
    db.create_all()
    db.session.execute(text("CREATE SEQUENCE IF NOT EXISTS joya_seq START 1"))
    db.session.commit()


@app.route("/admin/subir_joya", methods=["GET", "POST"])
def subir_joya():
    if request.method == "POST":
        tipo = request.form["tipo"]
        material = request.form["material"]
        diamante = "diamante" in request.form
        precio = request.form["precio"]
        descripcion = request.form["descripcion"]
        foto = request.files["foto"]

        # Guardar la foto en static/uploads
        filename = foto.filename
        foto.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        ruta_foto = f"/static/uploads/{filename}"

        nueva_joya = Joya(
            tipo=tipo,
            material=material,
            diamante=diamante,
            precio=precio,
            descripcion=descripcion,
            foto=ruta_foto
        )

        db.session.add(nueva_joya)
        db.session.commit()
        flash("Joya añadida correctamente")
        return redirect("/admin/subir_joya")

    return render_template("subir_joya.html")

def check_auth(username, password):
    """Verifica si el usuario y contraseña son correctos"""
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    """Devuelve un 401 solicitando autenticación básica"""
    return Response(
        "Autenticación requerida", 401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

@app.before_request
def require_auth():
    """Protege la ruta /admin/subir_joya con usuario/contraseña"""
    if request.endpoint == "subir_joya":
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

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

@app.route('/catalogo_joyas')
def catalogo_joyas():
    return render_template('catalogo_joyas.html')

if __name__ == "__main__":
    app.run(debug=True)


# compro oro. collar principal, anillos, efectivo, apreton de manos sin pistolas
# empeños. reloj fondo. taller, calendario, caja fuerte
# oro inversion. bolsa, oro
# venta joyas. escaparate joyas, chica joya, caja joyas