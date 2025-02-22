import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import base64
from dotenv import load_dotenv



class GeminiImageDescription:
    def __init__(self, api_key: str, model_name="gemini-2.0-flash",  delay=2):
        load_dotenv(dotenv_path="../.env")
        self.api_key = api_key
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
        Describe the image in one paragraph, covering the following aspects:

        Visual Elements: Focus on the main subjects—people, objects, or key features—including their appearance, colors, sizes, and placement in the frame.

        Setting/Environment: Note the location, time of day, weather, and any key background details (e.g., nature, architecture).

        Action/Emotion: Describe any actions, interactions, or emotional undertones in the image.

        Context/Story: Speculate on the story or context, and explain how the image makes you feel and why.

        Additional Details: Highlight any notable lighting, textures, angles, or symbolic elements.

        Be descriptive to offer a vivid picture while keeping it concise.
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
