from data_loader import ChromaDBClient, ChromaDBDataRetriever


class PathRetriever:
    def __init__(self, db_path="./db", collection_name="image_embeddings2"):
        # Initialize ChromaDBClient and ChromaDBDataRetriever
        self.db_client = ChromaDBClient(persist_directory=db_path)
        self.data_retriever = ChromaDBDataRetriever(
            client=self.db_client,
            collection_name=collection_name,
            include_embeddings=True,
            include_metadatas=True,
            include_documents=True
        )

    def fetch_image_paths(self):
        # Fetch all data from the collection
        data = self.data_retriever.get_all_data()
        image_paths = []

        for i in range(len(data["metadatas"])):
            image_paths.append(data["metadatas"][i]["image_path"])

        # Replace paths
        image_paths = [path.replace("../frontend/", "../") for path in image_paths]

        return image_paths


class MapThroughPath:
    """
    A class to transform and structure data by mapping image paths to their
    corresponding documents, tags, color palettes, and detected objects.

    The class processes metadata, splits comma-separated values into lists,
    and creates a new structured dictionary for easy access and further use.

    Attributes:
        data (dict): The input data containing 'metadatas' and 'documents' to be processed.
    """

    def __init__(self, data):
        """
        Initialize with the data to be transformed.

        Args:
            data (dict): The input data containing metadata and documents.
        """
        self.data = data

    def _split_metadata_field(self, metadata_field):
        """
        Helper method to split comma-separated metadata fields into lists.

        Args:
            metadata_field (str): The metadata field to be split into a list.

        Returns:
            list: A list of values split by commas.
        """
        return metadata_field.split(', ') if metadata_field else []

    def transform(self):
        """
        Transforms the input data by organizing and structuring it into a more accessible format.

        The method iterates over the metadata, extracts relevant information, splits metadata fields
        into lists, and maps the image path to its associated document, tags, color palette,
        and detected objects.

        Returns:
            dict: A dictionary with image paths as keys and structured data as values.
        """
        transformed_data = {}

        for idx, metadata in enumerate(self.data['metadatas']):
            path = metadata.get('image_path')
            image_path = path.replace("../frontend/", "../")
            document = self.data['documents'][idx]

            # Split the metadata fields into lists
            color_palette = self._split_metadata_field(metadata.get('color_palette', ''))
            detected_objects = self._split_metadata_field(metadata.get('detected_objects', ''))
            tags = self._split_metadata_field(metadata.get('tags', ''))

            # Structure the transformed data
            transformed_data[image_path] = {
                'document': document,
                'tags': tags,
                'color_palette': color_palette,
                'detected_objects': detected_objects
            }

        return transformed_data
