import shutil
import uuid

from fastapi import Depends, File, UploadFile
from starlette.responses import JSONResponse

from auth import get_current_user
from elastic_image import ImageElastic
from main import app
from models import Image, Image_Pydantic, User


@app.get("/images/")
async def get_images(search: str = None):
    return await Image_Pydantic.from_queryset(
        Image.filter(id__in=await ImageElastic.search(search))
        if search
        else Image.all()
    )


@app.get("/images/{image_id}/", response_model=Image_Pydantic)
async def get_image(image_id: int):
    return await Image_Pydantic.from_queryset_single(Image.get(id=image_id))


@app.post("/images/", response_model=Image_Pydantic)
async def create_image(
    title: str, user: User = Depends(get_current_user), image: UploadFile = File(...)
):
    file_path = f"/media/{str(uuid.uuid4())[:8]}_{image.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_obj = await Image.create(image=file_path, title=title, author_id=user.id)
    await ImageElastic(image_obj.id, title).create()

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
