import shutil
import uuid
from typing import List

from fastapi import Depends, File, UploadFile
from starlette.responses import JSONResponse

from auth import get_current_user
from elastic_image import ImageElastic
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
    await ImageElastic(image_obj.id, user.username, image_obj.image).create()

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


# ---------------------------------------------------------------------------


# @app.get("/func")
# async def func():
#     # resp: dict = await es.search(
#     #     index="documents",
#     #     body={"query": {"match_all": {}}},
#     #     size=20,
#     # )
#
#     await es.create(
#         index="images",
#         id=4,
#         body={"header": "Header of a new image", "link": "link of an image"},
#     )
#
#     return JSONResponse({"response": "task is done"})
#
#     # return JSONResponse(resp)
