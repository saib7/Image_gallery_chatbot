

from vectordb import ChromaDatabase


# Store images
db = ChromaDatabase(collection_name="image_embeddings2", persist_directory="./db")
db.store_images_in_chroma("../frontend/static/images")


# db.store_images_in_chroma("../gallery/images")
# db.reset_collection()
# # Example of querying with text
# print(db.query_with_text(query_text="A Girl"))
# print("\n\n")
#
# print(db.query_with_image("flowerGirl.jpg"))
