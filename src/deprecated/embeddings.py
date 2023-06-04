import json

# combine by concatenating
for i, (company, video_description, subtitles) in enumerate(data):
    for j, _ in enumerate(subtitles):
        if j < len(descriptions[i]):
            subtitles[j][-1] = (" ".join([subtitles[j][-1], descriptions[i][j]]))

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('flax-sentence-embeddings/all_datasets_v4_MiniLM-L6', device='cpu')
text = "Replace me by any text you'd like."
text_embbedding = model.encode(text)

description_data_time_ranges = [[] for _ in range(len(data))]
description_data = [[] for _ in range(len(data))]

for i, (_, _, subtitles) in enumerate(data):
    for t0, tf, descr in subtitles:
        description_data_time_ranges[i].append((t0, tf))
        description_data[i].append(descr)

embeddings = [[] for _ in range(len(data))]

for i, clip_descriptions in enumerate(description_data):
    video_description = data[i][1]
    for j, descr in enumerate(clip_descriptions):
        print(f"Creating embeddings for clip {i} | description: {j}")
        embeddings[i].append(model.encode(" ".join([descr, video_description])))

embeddings_path = os.path.join(CLEAN_DIR, "embeddings.pickle")

save_data(embeddings_path, embeddings)

embeddings = load_data(embeddings_path)

data = load_data(os.path.join(CLEAN_DIR, "data.pickle"))

data

import weaviate

client = weaviate.Client(url="http://localhost:8080")

schema = {
  "classes": [
    {
      "class": "A",
      "vectorizer": "none", # using precomputed embeddings
      "properties": [
        {
          "name": "t0",
          "dataType": ["number"]
        },
        {
          "name": "tf",
          "dataType": ["number"]
        },
        {
          "name": "filepath",
          "dataType": ["string"]
        }
      ]
    }
  ]
}


client.schema.create(schema)

clip_base_name = "clip_{}.mp4"

weaviate_objects = []
for i, (_, _, clip_data) in enumerate(data):
    for j in range(len(clip_data)):
        embedding = embeddings[i][j]
        if len(clip_data) != 0:
            obj = {
                "t0": clip_data[j][0],
                "tf": clip_data[j][1],
                "filepath": clip_base_name.format(i),
            }
            weaviate_objects.append((obj, embedding))


for obj, embedding in weaviate_objects:
    print(client.data_object.create(obj, "TPT", vector=embedding))

client.query.aggregate("TPT").with_meta_count().do()


query_text = "clean"
query_text_embedding = model.encode(query_text)

result = (
    client.query
    .get("TPT", ["t0", "tf", "filepath"])
    .with_near_vector({
        "vector": query_text_embedding,
        "certainty": 0.7
    })
    .with_limit(2)
    .do()
)

print(json.dumps(result, indent=4))