import os
import time
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate


class ImageMetadata(BaseModel):
    description: str = Field(description="A short detailed description of the image's content")
    detected_objects: list[str] = Field(description="A list of objects detected in the image")
    color_palette: list[str] = Field(description="A list of predominant colors in the image")
    potential_use_cases: list[str] = Field(description="Potential use cases or industries that could benefit from the image")
    tags: list[str] = Field(description="Relevant tags for categorizing the image")


class ImageAnalyzer:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite-preview-02-05", delay: int = 2):
        load_dotenv(dotenv_path="../.env")
        self.api_key = api_key
        self.delay = delay
        self.model = ChatGoogleGenerativeAI(model=model_name, api_key=self.api_key)
        self.parser = PydanticOutputParser(pydantic_object=ImageMetadata)
        self.prompt = self._create_prompt_template()

    def _create_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system",
             "Analyze the provided image and generate professional metadata in the following structure: short description, detected objects, color palette, potential use cases, and tags. Provide the metadata in {language}.\n'{format_instructions}'\n"),
            ("human", [
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,{image_data}"},
                },
            ])
        ])

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        return image_data

    def analyze_image(self, image_path: str, language: str = "English") -> str:
        image_data = self._encode_image(image_path)

        chain = self.prompt | self.model | self.parser

        time.sleep(self.delay)
        result = chain.invoke({
            "language": language,
            "format_instructions": self.parser.get_format_instructions(),
            "image_data": image_data
        })

        return result.model_dump()

