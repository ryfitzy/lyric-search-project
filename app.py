import os
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

es = Elasticsearch(
  os.environ.get("URL"),
  api_key=os.environ.get("SECRET_KEY")
)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form["query"]
        results = es.search(index="songs", query={
            "multi_match": {
                "query": query,
                "fields": ["title", "artist", "lyrics"]
            }
        }, highlight={
            "fields": {
                "lyrics": {
                    "fragment_size": 150,
                    "number_of_fragments": 1
                }
            }
        })
        hits = []
        for hit in results["hits"]["hits"]:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            snippet = highlight.get("lyrics", [source["lyrics"][:200] + "..." if source.get("lyrics") else "No lyrics available."])[0]

            hits.append({
                "id": hit["_id"],
                "title": source["title"],
                "rank": source.get("rank", "N/A"),
                "year": source.get("year", "Unknown"),
                "artist": source["artist"],
                "snippet": snippet
            })
        return render_template("results.html", query=query, results=hits)
    return render_template("index.html")


@app.route("/song/<id>")
def song_detail(id):
    song = es.get(index="songs", id=id)["_source"]
    return render_template("song_detail.html", song=song)

if __name__ == "__main__":
    app.run(debug=True)

