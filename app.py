from flask import Flask, render_template, request, flash, redirect, abort, jsonify
from flask_wtf import FlaskForm
from InputForm import InputForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = "Mg#i8t!@Rd6"

shortened_urls = []

# Define a data structure for storing metadata about short URLs
url_metadata = {}

@app.route("/", methods=["GET", "POST"])
def home():
    form = InputForm()
    if request.method == "POST":
        if form.validate_on_submit():
            id = secrets.token_urlsafe(8)
            shortened_url = request.base_url + id
            shortened_urls.append({"destination_url": form.url.data, "id": id})
            url_metadata[id] = {"destination_url": form.url.data, "hits": 0}
            flash(f"Shortened URL: {shortened_url}", "success message")
            form.url.data = ''
        else:
            flash("Invalid URL!", "error message")
    return render_template("index.html", form=form)

@app.route("/<id>")
def shortened(id):
    for shortened_url in shortened_urls:
        if shortened_url["id"] == id:
            url_metadata[id]["hits"] += 1
            return redirect(shortened_url["destination_url"])
    return abort(404)

# New API endpoint to create short URLs
@app.route("/api/create", methods=["POST"])
def api_create_short_url():
    data = request.get_json()
    long_url = data.get('long_url')

    if long_url:
        id = secrets.token_urlsafe(8)
        short_url = request.base_url + id
        shortened_urls.append({"destination_url": long_url, "id": id})
        url_metadata[id] = {"destination_url": long_url, "hits": 0}
        return jsonify({"short_url": short_url})
    else:
        return jsonify({"error": "Invalid request"}), 400

# New API endpoint to search for URLs by title
@app.route("/api/search", methods=["GET"])
def api_search_url():
    term = request.args.get('term')
    results = []
    for id, metadata in url_metadata.items():
        if term.lower() in metadata['destination_url'].lower():
            result = {
                'title': metadata['destination_url'],
                'url': request.base_url + id,
                'hits': metadata['hits']
            }
            results.append(result)
    return jsonify(results)

# New API endpoint to get metadata for a short URL
@app.route("/api/metadata/<id>", methods=["GET"])
def api_get_metadata(id):
    if id in url_metadata:
        metadata = url_metadata[id]
        return jsonify({
            'title': metadata['destination_url'],
            'hits': metadata['hits']
        })
    else:
        return jsonify({"error": "Short URL not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
