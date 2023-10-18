from flask import Flask, render_template, redirect, request

app = Flask(__name__)
shortened_url = {}


def generate_short_url(lenght=6):
    import random
    import string
    char = string.ascii_letters + string.digits
    short_url = "".join(random.choice(char) for _ in range(lenght))

    return short_url


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form['long_url']
        short_url = request.form.get('short_url')
        if short_url:
            if not short_url in shortened_url:
                shortened_url[short_url] = long_url
            else:
                return "This short URL already exists!"
        else:
            short_url = generate_short_url()
            while short_url in shortened_url:
                short_url = generate_short_url()

            shortened_url[short_url] = long_url
        return f"Shortened URL: {request.url_root}{short_url}"
    return render_template("index.html")


@app.route('/<short_url>')
def redirect_url(short_url):
    long_url = shortened_url.get(short_url)
    if long_url:
        return redirect(long_url)
    else:
        return "URL not found", 404


if __name__ == '__main__':
    app.run(debug=True)