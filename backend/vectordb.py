import chromadb
import os
import torch
import numpy as np
from dotenv import load_dotenv

from embedings import CLIPEmbedding
from chromadb import errors
from description_ai import GeminiImageDescription
from metadata_ai import ImageAnalyzer
from pathlib import Path
load_dotenv(dotenv_path="../.env")


class ChromaDatabase:
    def __init__(self, collection_name="image_embeddings", persist_directory="./chroma_db"):
        """
        Initializes the ChromaImageDatabase object with a Chroma client and
        attempts to get or create the specified collection.
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        # self.collection = self._get_or_create_collection()
        self.collection = self.client.get_or_create_collection(self.collection_name)

        # Initialize AI components with API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        self.clip_embedding = CLIPEmbedding()
        self.description = GeminiImageDescription(api_key, delay=5)
        self.meta_data = ImageAnalyzer(api_key, delay=5)


    def _get_or_create_collection(self):
        """
        Tries to fetch the existing collection, creates a new one if it doesn't exist.
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            print("Collection found.")
        except chromadb.errors.InvalidCollectionException:
            print("Collection does not exist, creating...")
            collection = self.client.create_collection(self.collection_name)
        return collection

    def store_image_in_db(self, image_path: str):
        """
    Stores an image embedding in the Chroma vector database only if it doesn't already exist.

    Args:
    - image_path (str): Path to the image file.
    - collection (chromadb.Collection): The Chroma collection to store the image in.
    """
        image_embedding = self.clip_embedding.embed_image(image_path)
        image_name = os.path.basename(image_path)
        image_id = os.path.splitext(image_name)[0]

        # Check if the image ID already exists in the collection
        existing_docs = self.collection.get(ids=[image_id])

        if existing_docs['ids']:
            # If a matching document exists, do not add it again
            print(f"Image {image_name} already exists in the collection. Skipping...")
            return

        image_description = self.description.get_description(image_path)
        image_metadata = self.meta_data.analyze_image(image_path=image_path, language="English")

        # Convert list fields to comma-separated strings
        chroma_compatible_metadata = {
            "image_path": Path(image_path).as_posix(),  # Add the full image path to metadata
            "detected_objects": ", ".join(image_metadata["detected_objects"]),
            "color_palette": ", ".join(image_metadata["color_palette"]),
            "potential_use_cases": ", ".join(image_metadata["potential_use_cases"]),
            "tags": ", ".join(image_metadata["tags"])
        }

        # Store the image embedding in Chroma DB
        self.collection.add(
            documents=[image_description],  # You can store any metadata, here we use the image name
            metadatas=[chroma_compatible_metadata],
            embeddings=[image_embedding],
            ids=[image_id]  # Use the unique ID here
        )

    def store_images_in_chroma(self, image_directory: str):
        """
    This method iterates through all the images in the specified directory,
    generates embeddings for each image using CLIP, and stores them in a Chroma vector database.
    """
        for image_filename in os.listdir(image_directory):
            image_path = os.path.join(image_directory, image_filename)

            if image_filename.endswith(('jpg', 'png', 'jpeg')):  # Check for valid image formats
                print(f"Processing {image_filename}...")
                self.store_image_in_db(image_path)

        print("All images have been processed and stored in Chroma. Collection Name: ", self.collection_name)

    def reset_collection(self):
        """
        Resets the collection by deleting it from the database.
        After calling this method, the collection will be empty.
        """
        if self.collection_name in self.client.list_collections():
            self.client.delete_collection(self.collection_name)
            print(f"Collection {self.collection_name} has been reset.")
            # Recreate the collection after deletion
            self.collection = self.client.get_or_create_collection(self.collection_name)
        else:
            print(f"Collection {self.collection_name} does not exist.")


    def query_with_text(self, query_text=None, top_k=5):
        """
            Queries a database using a text input by generating an embedding for the text
            and retrieving the most relevant results based on the generated embedding.

            Args:
                query_text (str): The text query to search for. Defaults to None.
                top_k (int): The number of top results to retrieve. Defaults to 5.

            Returns:
                list: A list of the most relevant documents from the database based on the query.
            """
        # Process text query and generate text embedding using CLIP
        text_embedding = self.clip_embedding.embed_text(query_text)

        # Query the database based on text embedding
        results = self.collection.query(query_embeddings=text_embedding, n_results=top_k)
        return results['documents'], results['metadatas']

    def query_with_image(self, query_image=None, top_k=5):
        """
            Queries a database using an image input by generating an embedding for the image
            and retrieving the most relevant results based on the generated embedding.

            Args:
                query_image: Path of the image to search for similar image, Defaults to None.
                top_k (int, optional): The number of top results to retrieve. Defaults to 5.

            Returns:
                list: A list of the most relevant documents from the database based on the image query.
            """

        # Generate image embedding for image query
        image_embedding = self.clip_embedding.embed_image(query_image)

        # Query the database based on image embedding
        results = self.collection.query(query_embeddings=image_embedding, n_results=top_k)
        return results['documents'], results['metadatas']

    def query_with_text_and_image(self, query_text=None, query_image=None, top_k=5):

        # Validate input
        if not query_text and not query_image:
            return "Please provide both query_text and query_image."

        # Initialize embeddings list
        combined_embeddings = []

        # Process text query and generate text embedding using CLIP

        text_embedding = self.clip_embedding.embed_text(query_text)
        combined_embeddings.append(text_embedding)

        # Generate image embedding for image query
        image_embedding = self.clip_embedding.embed_image(query_image)
        combined_embeddings.append(image_embedding)

        combined_embeddings_mean = np.mean(combined_embeddings, axis=0)

        results = self.collection.query(query_embeddings=combined_embeddings_mean , n_results=top_k)
        return results['documents'], results['metadatas']

