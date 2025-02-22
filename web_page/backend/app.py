from flask import Flask, render_template, redirect, request
import os

app = Flask(__name__,
            template_folder=os.path.join(os.getcwd(), 'frontend'),
            static_folder=os.path.join(os.getcwd(), 'frontend', 'static'))

# Ruta principal (home)
@app.route("/")
def home():
    if request.host.startswith("www."):
        return redirect("https://lacentraldeloro.com", code=301)
    return render_template("index.html")

# Ruta de ejemplo
@app.route("/about")
def about():
    return "Esta es la página 'About'."

if __name__ == "__main__":
    app.run(debug=True)