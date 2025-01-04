from flask import Flask, render_template

app = Flask(__name__)

# Ruta principal (home)
@app.route("/")
def home():
    return render_template("index.html")

# Ruta de ejemplo
@app.route("/about")
def about():
    return "Esta es la página 'About'."

if __name__ == "__main__":
    app.run(debug=True) 
