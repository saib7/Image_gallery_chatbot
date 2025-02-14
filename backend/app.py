from embedings import CLIPEmbedding
from vectordb import ChromaDatabase


db = ChromaDatabase(collection_name="image_embeddings2", persist_directory="./db")

# Do some query
# Example of querying with text
print(db.query_with_text(query_text="A Girl with flower"))
print("\n\n")

print(db.query_with_image("flowerGirl.jpg"))
print("\n\n")

print(db.query_with_text_and_image(query_text="A Girl with flower", query_image="flowerGirl.jpg"))
