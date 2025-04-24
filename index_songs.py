import os
import pandas as pd
from elasticsearch import Elasticsearch

es = Elasticsearch(
  os.environ.get("URL"),
  api_key=os.environ.get("SECRET_KEY")
)

lyrics = pd.read_csv("lyrics.csv", encoding="ISO-8859-1")

index_name = "songs"

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

es.indices.create(index=index_name)

for i, row in lyrics.iterrows():
    source_val = row["Source"]
    doc = {
        "rank": None if pd.isna(row["Rank"]) else int(row["Rank"]),
        "title": row["Song"],
        "artist": row["Artist"],
        "year": int(row["Year"]),
        "lyrics": None if pd.isna(row["Lyrics"]) else row["Lyrics"],
        "source": None if pd.isna(row["Source"]) else row["Source"],
    }
    es.index(index="songs", id=i, document=doc)

print("✅ Indexed all songs to Elastic Cloud!")

