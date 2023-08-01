import random
import string

from flask import Flask, render_template, redirect, url_for, request

app =Flask(__name__)
shortened_url = {}

def generate_short_url(lenght=6):
    char = string.ascii_letters + string.digits
    short_url = "".join(random.choice(char) for _ in range(lenght))

    return short_url

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form['long_url']
        short_url = generate_short_url()
        while short_url in shortened_url:
            short_url = generate_short_url()

        shortened_url[short_url] = long_url
        return f"Shortened URL: {request.url_root}{short_url}"
    return render_template("templates/index.html")