from embedings import CLIPEmbedding
from vectordb import ChromaDatabase
from description_ai import GeminiImageDescription
from metadata_ai import ImageAnalyzer
from dotenv import load_dotenv
import os

import warnings
warnings.filterwarnings("ignore")

db = ChromaDatabase(collection_name="image_embeddings2", persist_directory="./db")
#
# # Do some query
# # Example of querying with text
print(db.query_with_text(query_text="A Girl with flower"))
print("\n\n")
#
# print(db.query_with_image("flowerGirl.jpg"))
# print("\n\n")
#
# print(db.query_with_text_and_image(query_text="A Girl with flower", query_image="flowerGirl.jpg"))

# image_path = "flowerGirl.jpg"
# image_description = GeminiImageDescription()
# description = image_description.get_description(image_path)
# print(description)


# image_path = "flowerGirl.jpg"
# load_dotenv(dotenv_path="../.env")
# api_key = os.getenv("GEMINI_API_KEY")
# analyzer = ImageAnalyzer(api_key=api_key)
# metadata = analyzer.analyze_image(image_path=image_path, language="English")
# print(metadata)
