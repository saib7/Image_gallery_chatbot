from embedings import CLIPEmbedding
from vectordb import ChromaDatabase
from description_ai import GeminiImageDescription
from metadata_ai import ImageAnalyzer
from dotenv import load_dotenv
import os
from data_loader import ChromaDBClient, ChromaDBDataRetriever

import warnings
warnings.filterwarnings("ignore")

# db = ChromaDatabase(collection_name="image_embeddings2", persist_directory="./db")
#
# # Do some query
# # Example of querying with text
# path, meta = db.query_with_text(query_text="A Girl with flower")
# print(path)
# print("\n\n")
# print(meta)
# print(db.query_with_text(query_text="A Girl with flower"))
# print("\n\n")

# print(db.query_with_image("flowerGirl.jpg"))
# print("\n\n")
#
# print(db.query_with_text_and_image(query_text="A Girl with flower", query_image="flowerGirl.jpg"))

db_client = ChromaDBClient(persist_directory="./db")
data_retriever = ChromaDBDataRetriever(
    client=db_client,
    collection_name="image_embeddings2",
    include_embeddings=True,
    include_metadatas=True,
    include_documents=True
)

# Fetch all data from the collection
data = data_retriever.get_all_data()

# data_dict = {"image_path": [], "metadata": []}
print(data)





# data['path'] = data['documents']

# # Print the results
# print("Fetched Data:")
# for key, value in data.items():
#     if key == 'metadatas':
#         print(f"{key}: {value}")
