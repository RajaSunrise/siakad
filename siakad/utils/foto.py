from uuid import uuid4
from PIL import Image

from fastapi import UploadFile


async def save_avatar(file: UploadFile):
    # Generate unique filename
    filename = f"{uuid4().hex}.jpg"

    # Save file to uploads directory
    with open(f"uploads/{filename}", "wb") as f:
        f.write(await file.read())

    # Resize image to thumbnail
    with Image.open(f"uploads/{filename}") as img:
        img.thumbnail((128, 128))
        img.save(f"uploads/thumbs/{filename}")

    return filename
