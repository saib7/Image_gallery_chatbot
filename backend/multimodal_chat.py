import os
import time
import base64
from typing import List, Literal, Optional, Union
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import your existing components
from vectordb import ChromaDatabase


class MultimodalRAGChat:
    """
    A multimodal chat system with Retrieval-Augmented Generation (RAG) capabilities.

    This class combines image analysis, text analysis, and vectorized data retrieval
    to provide contextually relevant responses using the Gemini 2.0 Flash model.

    Attributes:
        api_key (str): The Google Gemini API key
        model_name (str): The Gemini model to use
        vector_db (ChromaDatabase): Vector database for embeddings and retrieval
        llm (ChatGoogleGenerativeAI): The language model for generating responses
        memory (ConversationBufferMemory): Memory to maintain conversation context
        retrieval_chain (ConversationalRetrievalChain): Chain for retrieving information
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash",
                 collection_name: str = "image_embeddings",
                 persist_directory: str = "./chroma_db"):
        """
        Initialize the MultimodalRAGChat system.

        Args:
            api_key (str): Google Gemini API key
            model_name (str): Name of the Gemini model to use
            collection_name (str): Name of the ChromaDB collection for vector storage
            persist_directory (str): Directory to persist ChromaDB data
        """
        self.api_key = api_key
        self.model_name = model_name

        # Initialize vector database with existing code
        self.vector_db = ChromaDatabase(
            collection_name=collection_name,
            persist_directory=persist_directory
        )

        # Initialize the language model for chat
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0.8,
        )


        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Create a conversational retrieval chain
        self._initialize_retrieval_chain()

        # Keep track of the conversation history
        self.chat_history = []


    def _initialize_retrieval_chain(self):
        """
        Initialize the retrieval chain for RAG capabilities.
        """
        # Create a retriever from the Chroma collection
        retriever = self.vector_db.collection.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # System prompt to guide the model
        system_prompt = """
        You are a helpful assistant with multimodal capabilities.
        Use the retrieved context to provide informative and accurate responses.
        When image information is present in the context, use it to enhance your response.
        Maintain a conversational and natural tone throughout the interaction.
        """

        # Create the RAG prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
            ("system", "Context information for answering the question: {context}")
        ])

        # Create the retrieval chain
        self.retrieval_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True
        )


    def _encode_image(self, image_path: str) -> str:
        """
        Encode an image to base64 format.

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Base64 encoded image data
        """
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                return image_data
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None


    def process_message(self,
                        text_query: Optional[str] = None,
                        image_path: Optional[str] = None,
                        text_weight: float = 0.5,
                        image_weight: float = 0.5) -> dict:
        """
        Process a user message that may contain text, image, or both.

        Args:
            text_query (Optional[str]): Text query from the user
            image_path (Optional[str]): Path to an image if provided
            text_weight (float): Weight for text query in combined searches (0.0-1.0)
            image_weight (float): Weight for image query in combined searches (0.0-1.0)

        Returns:
            dict: Response containing the assistant's message and any retrieved context
        """
        # Perform retrieval based on the type of query
        retrieval_results = None
        if text_query and image_path:
            # Combined text and image query
            retrieval_results = self.vector_db.query_with_text_and_image(
                query_text=text_query,
                query_image=image_path,
                top_k=3,
                text_weight=text_weight,
                image_weight=image_weight
            )
        elif text_query:
            # Text-only query
            retrieval_results = self.vector_db.query_with_text(
                query_text=text_query,
                top_k=3
            )
        elif image_path:
            # Image-only query
            retrieval_results = self.vector_db.query_with_image(
                query_image=image_path,
                top_k=3
            )
        else:
            # No query provided
            return {"response": "Please provide a text query or image to search."}

        # Prepare context from retrieved documents
        context_docs = []
        if retrieval_results:
            for i, doc in enumerate(retrieval_results['documents'][0]):
                metadata = retrieval_results['metadatas'][0][i]
                context_docs.append(
                    f"Document {i + 1}:\n"
                    f"Description: {doc}\n"
                    f"Detected Objects: {metadata.get('detected_objects', 'None')}\n"
                    f"Tags: {metadata.get('tags', 'None')}\n"
                    f"Potential Use Cases: {metadata.get('potential_use_cases', 'None')}\n"
                )

        context = "\n\n".join(context_docs)

        # If there's an image in the query, create a multimodal message
        user_message = text_query or "Describe this image"
        if image_path:
            # Prepare the image for Gemini if needed
            image_data = self._encode_image(image_path)

            # Record the message in chat history
            image_message = HumanMessage(
                content=[
                    {"type": "text", "text": user_message},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ]
            )
            self.chat_history.append(image_message)

            # For the retrieval chain, we need to use text only
            query = f"{user_message} [IMAGE QUERY]"
        else:
            # Regular text message
            self.chat_history.append(HumanMessage(content=user_message))
            query = user_message

        # Get response from the retrieval chain
        response = self.retrieval_chain({"question": query, "context": context, "chat_history": self.chat_history})

        # Add AI response to history
        self.chat_history.append(AIMessage(content=response["answer"]))

        return {
            "response": response["answer"],
            "retrieved_context": context,
            "source_documents": response.get("source_documents", [])
        }

    def upload_image_to_db(self, image_path: str) -> str:
        """
        Upload a single image to the vector database.

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Status message
        """
        try:
            self.vector_db.store_image_in_db(image_path)
            return f"Successfully uploaded image: {os.path.basename(image_path)}"
        except Exception as e:
            return f"Error uploading image: {e}"

    def upload_image_directory(self, directory_path: str) -> str:
        """
        Upload all images from a directory to the vector database.

        Args:
            directory_path (str): Path to directory containing images

        Returns:
            str: Status message
        """
        try:
            if not os.path.exists(directory_path):
                return f"Directory not found: {directory_path}"

            self.vector_db.store_images_in_chroma(directory_path)
            return f"Successfully processed all images in {directory_path}"
        except Exception as e:
            return f"Error processing directory: {e}"

    def reset_chat_history(self):
        """Reset the conversation history."""
        self.chat_history = []
        self.memory.clear()

    def reset_vector_db(self):
        """Reset the vector database collection."""
        self.vector_db.reset_collection()
        return "Vector database collection has been reset."




