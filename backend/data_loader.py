import chromadb
from typing import Dict, List, Optional


class ChromaDBClient:
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the ChromaDB client.

        Args:
            persist_directory (Optional[str]): Path to the persistent database directory. If None, uses in-memory.
        """
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()

    def get_collection(self, collection_name: str):
        """
        Get a specific collection from the database.

        Args:
            collection_name (str): Name of the collection to fetch.

        Returns:
            collection: The collection object.
        """
        return self.client.get_collection(name=collection_name)


class ChromaDBDataRetriever:
    def __init__(
            self,
            client: ChromaDBClient,
            collection_name: str,
            include_embeddings: bool = False,
            include_metadatas: bool = True,
            include_documents: bool = True
    ):
        """
        Initialize the ChromaDBDataRetriever instance.

        Args:
            client (ChromaDBClient): The ChromaDB client instance.
            collection_name (str): The name of the collection to fetch data from.
            include_embeddings (bool): Whether to include embeddings in the results.
            include_metadatas (bool): Whether to include metadata in the results.
            include_documents (bool): Whether to include documents in the results.
        """
        self.client = client
        self.collection_name = collection_name
        self.include_embeddings = include_embeddings
        self.include_metadatas = include_metadatas
        self.include_documents = include_documents

    def get_all_data(self) -> Dict[str, List]:
        """
        Retrieve all data from the ChromaDB collection.

        Returns:
            Dict[str, List]: A dictionary containing the fetched data (ids, embeddings, metadatas, documents).
        """
        try:
            # Access the collection
            collection = self.client.get_collection(self.collection_name)

            # Prepare the options for fetching data
            include_options = []
            if self.include_embeddings:
                include_options.append("embeddings")
            if self.include_metadatas:
                include_options.append("metadatas")
            if self.include_documents:
                include_options.append("documents")

            # Fetch all data from the collection
            results = collection.get(include=include_options)

            return results

        except Exception as e:
            print(f"An error occurred: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    # Initialize ChromaDB client with a persistent directory (optional)
    chroma_client = ChromaDBClient(persist_directory="/path/to/persist/directory")  # Optional

    # Initialize ChromaDB data retriever for a specific collection
    data_retriever = ChromaDBDataRetriever(
        client=chroma_client,
        collection_name="my_collection",
        include_embeddings=True,
        include_metadatas=True,
        include_documents=True
    )

    # Fetch all data from the collection
    data = data_retriever.get_all_data()

    # Print the results
    print("Fetched Data:")
    for key, value in data.items():
        print(f"{key}: {value}")
