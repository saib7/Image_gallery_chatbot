## To DO:
## Need To solve file import path problems


from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import os
import sys

sys.path.append("")

from data_loader import ChromaDBClient, ChromaDBDataRetriever
from utility import PathRetriever, MapThroughPath

# # Ensure static/images directory exists
if not os.path.exists('../frontend/static/images'):  # Directory check and creation
    os.makedirs('../frontend/static/images')

# Create the FastAPI
app = FastAPI()

templates = Jinja2Templates(directory="../frontend/templates")
# Serve static files like images, CSS, and JS from the 'static' folder
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the homepage (HTML content) for the MemoryBot website.

    The homepage consists of a Hero section, Features section, and Footer.
    This function renders the HTML content as a response.

    Args:
        request (Request): The incoming request object.

    Returns:
        HTMLResponse: Renders the homepage HTML content.
    """

    return templates.TemplateResponse("home_page.html", {"request": request})


@app.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request):
    get_path = PathRetriever(db_path="./db", collection_name="image_embeddings2")
    image_paths = get_path.fetch_image_paths()

    return templates.TemplateResponse("gallery.html", {"request": request, "image_paths": image_paths})


@app.get("/image-viewer", response_class=HTMLResponse)
async def image_viewer(request: Request, image: str = None):
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
    map_through_path = MapThroughPath(data)
    formatted_data = map_through_path.transform()
    descriptions = formatted_data[image]["document"]
    tags = formatted_data[image]["tags"]
    color_palette = formatted_data[image]["color_palette"]
    detected_objects = formatted_data[image]["detected_objects"]

    return templates.TemplateResponse("image-viewer.html",
                                      {"request": request, "image_path": image, "description": descriptions,
                                       "tags": tags, "color_palette": color_palette,
                                       "detected_objects": detected_objects})


@app.get("/uploader", response_class=HTMLResponse)
async def uploader(request: Request):
    return templates.TemplateResponse("uploader.html", {"request": request})


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Handle multiple image uploads and save them to the static/images directory.

    Args:
        files (List[UploadFile]): List of uploaded image files.

    Returns:
        dict: Message indicating success or failure.
    """
    for file in files:
        upload_path = f"../frontend/static/images/{file.filename}"
        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())

    return {"message": f"{len(files)} files successfully uploaded!"}

