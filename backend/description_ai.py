import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import base64
from dotenv import load_dotenv


load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GEMINI_API_KEY")


class GeminiImageDescription:
    def __init__(self, model_name="gemini-2.0-flash-lite-preview-02-05", delay=2):
        self.model_name = model_name
        self.model = ChatGoogleGenerativeAI(model=self.model_name, api_key=api_key)
        self.delay = delay


    def load_image(self, image_path: str):
        """Reads and encodes the image from the local path."""
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            return image_data
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def create_message(self, image_data):
        """Creates a HumanMessage with the encoded image."""

        text = """
        Please provide a detailed and comprehensive description of the following image. Your response should include the following elements:

        Visual Elements: Describe the main objects, people, or subjects in the image, including their appearance, color, size, and position within the frame.

        Setting/Environment: Describe the environment or background, including location, time of day, weather, and any notable details (such as buildings, nature, or interior design).

        Action/Emotion: If there are any actions or interactions happening in the image, describe them. Also, include any emotions or moods that can be inferred from the people or objects in the image.

        Context/Story: If applicable, speculate on the context or story behind the image. What might be happening before or after this moment? How does the image make you feel, and why?

        Additional Details: Mention any other distinctive features like lighting, textures, or angles that stand out. Feel free to include symbolic interpretations or insights related to the image.

        Be as descriptive and detailed as possible to provide a vivid understanding of the image. But write everything in one or two paragraph.
        """

        return HumanMessage(
            content=[
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ],
        )

    def invoke_model(self, message):
        """Invoke the model with the message and return the response."""
        # Introducing a delay to prevent sending too many requests in a short period of time
        time.sleep(self.delay)
        return self.model.invoke([message])

    def get_description(self, image_path: str):
        """Invokes the model and retrieves the description of the fruit."""
        image_data = self.load_image(image_path)
        if image_data:
            message = self.create_message(image_data)
            response = self.invoke_model(message)
            return response.content
        else:
            return "Failed to load the image."

