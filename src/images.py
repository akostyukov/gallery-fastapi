import shutil
import uuid
from typing import List

from fastapi import Depends, File, UploadFile
from starlette.responses import FileResponse, JSONResponse

from auth import get_current_user
from main import app
from models import Image, Image_Pydantic, User


@app.get("/images/", response_model=List[Image_Pydantic])
async def get_images():
    return await Image_Pydantic.from_queryset(Image.all())


@app.get("/images/{image_id}/", response_model=Image_Pydantic)
async def get_image(image_id: int):
    return await Image_Pydantic.from_queryset_single(Image.get(id=image_id))


@app.post("/images/", response_model=Image_Pydantic)
async def create_image(
    user: User = Depends(get_current_user), image: UploadFile = File(...)
):
    file_path = f"/media/{str(uuid.uuid4())[:8]}_{image.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_obj = await Image.create(image=file_path, author_id=user.id)
    return await Image_Pydantic.from_tortoise_orm(image_obj)


@app.post("/images/{image_id}/like")
async def like(image_id: int, user: User = Depends(get_current_user)):
    image = await Image.get(id=image_id).prefetch_related("likes")

    if user in image.likes:
        await image.likes.remove(user)
        response = "unset"
    else:
        await image.likes.add(user)
        response = "set"

    return JSONResponse({"success": f"like has been {response}"})


@app.get("/image-file/{image_id}/")
async def image_file(image_id: int):
    image = await Image.get(id=image_id)
    return FileResponse(image.image)
