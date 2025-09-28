from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, text
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Railway lo pone automáticamente
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

# Modelo Joya + ID automático
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

# Crear tablas y secuencia al arrancar
with app.app_context():
    db.create_all()
    db.session.execute(text("CREATE SEQUENCE IF NOT EXISTS joya_seq START 1"))
    db.session.commit()
