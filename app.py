from flask import Flask, render_template, redirect, request, jsonify
from flask_mysqldb import MySQL
import random
import string

app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'linkshortener_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


def generate_short_url(lenght=6):
    char = string.ascii_letters + string.digits
    return "".join(random.choice(char) for _ in range(lenght))


def add_https_protocol(url):
    return url if url.startswith("https://") else "https://" + url


def get_url(short_url):
    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE short_url = %s", [short_url])
    return cursor.fetchone()


def insert_url(short_url, long_url):
    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("INSERT INTO urls (short_url, long_url) VALUES (%s, %s)", [short_url, long_url])
    conn.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = add_https_protocol(request.form['long_url'])
        short_url = request.form.get('short_url', generate_short_url())

        if get_url(short_url):
            return "This short URL already exists!"
        else:
            insert_url(short_url, long_url)
            return render_template("result.html", short_url=f"{request.url_root}{short_url}")

    return render_template("index.html")


@app.route("/<short_url>")
def redirect_url(short_url):
    data = get_url(short_url)
    return redirect(data["long_url"]) if data else ("URL not found", 404)


@app.route("/api/url", methods=["POST"])
def create_url():
    long_url = request.json["long_url"]
    short_url = request.json.get("short_url", generate_short_url())

    if get_url(short_url):
        return jsonify({"error": "This short URL already exists!"}), 400
    else:
        insert_url(short_url, long_url)
        return jsonify({"short_url": f"{request.url_root}{short_url}"}), 201


if __name__ == "__main__":
    app.run(debug=True)