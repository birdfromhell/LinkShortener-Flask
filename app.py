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
    short_url = "".join(random.choice(char) for _ in range(lenght))
    return short_url


def add_https_protocol(url):
    if not url.startswith("https://"):
        url = "https://" + url
    return url


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        long_url = request.form['long_url']
        long_url = add_https_protocol(long_url)
        short_url = request.form.get('short_url')

        conn = mysql.connect
        cursor = conn.cursor()

        if short_url:
            query = "SELECT * FROM urls WHERE short_url = '%s'" % short_url
            cursor.execute(query)
            data = cursor.fetchone()
            if not data:
                query = "INSERT INTO urls (short_url, long_url) VALUES ('%s', '%s')" % (short_url, long_url)
                cursor.execute(query)
                conn.commit()
            else:
                error = "This short URL already exists!"
                return render_template("index.html", error=error)
        else:
            short_url = generate_short_url()
            query = "SELECT * FROM urls WHERE short_url = '%s'" % short_url
            while cursor.execute(query):
                short_url = generate_short_url()
                query = "SELECT * FROM urls WHERE short_url = '%s'" % short_url

            query = "INSERT INTO urls (short_url, long_url) VALUES ('%s', '%s')" % (short_url, long_url)
            cursor.execute(query)
            conn.commit()

        full_short_url = f"{request.url_root}{short_url}"
        return render_template("result.html", short_url=full_short_url)

    return render_template("index.html", error=error)


@app.route("/<short_url>")
def redirect_url(short_url):
    conn = mysql.connect
    cursor = conn.cursor()

    query = "SELECT * FROM urls WHERE short_url = '%s'" % short_url
    cursor.execute(query)
    data = cursor.fetchone()

    if data:
        return redirect(data["long_url"])
    else:
        return "URL not found", 404


@app.route("/api/url", methods=["POST"])
def create_url():
    long_url = request.json["long_url"]
    short_url = request.json.get("short_url")

    conn = mysql.connect
    cursor = conn.cursor()

    if short_url:
        query = "SELECT * FROM urls WHERE short_url = '%s'" % short_url
        cursor.execute(query)
        data = cursor.fetchone()

        if not data:
            query = "INSERT INTO urls (short_url, long_url) VALUES ('%s', '%s')" % (short_url, long_url)
            cursor.execute(query)
            conn.commit()
        else:
            return jsonify({"error": "This short URL already exists!"}), 400
    else:
        short_url = generate_short_url()
        query = "SELECT * FROM urls WHERE short_url = '%s'" % short_url
        while cursor.execute(query):
            short_url = generate_short_url()
            query = "SELECT * FROM urls WHERE short_url = '%s'" % short_url

        query = f"INSERT INTO urls (short_url, long_url) VALUES ('{short_url}', '{long_url}')"
        cursor.execute(query)
        conn.commit()

    return jsonify({"short_url": f"{request.url_root}{short_url}"}), 201


if __name__ == "__main__":
    app.run(debug=True)