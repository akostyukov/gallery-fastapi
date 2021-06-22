import shutil
import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from auth import get_current_user
from elastic_image import ImageElastic
from models import Image, Image_Pydantic, User

images_router = APIRouter(prefix="/images", tags=["Images"])


@images_router.get("/")
async def get_images(search: str = None):
    params = dict()

    if search:
        params["id__in"] = await ImageElastic.search(search)

    return await Image_Pydantic.from_queryset(Image.filter(**params))


@images_router.get("/{image_id}/", response_model=Image_Pydantic)
async def get_image(image_id: int):
    return await Image_Pydantic.from_queryset_single(Image.get(id=image_id))


@images_router.get("/media/{image_id}/")
async def get_media(image_id: int):
    return FileResponse((await Image.get(id=image_id)).image)


@images_router.post("/")
async def create_image(
    title: str, image: UploadFile = File(...), user: User = Depends(get_current_user)
):
    file_path = f"../media/{str(uuid.uuid4())[:8]}_{image.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_obj = await Image.create(image=file_path, title=title, author_id=user.id)
    await ImageElastic(image_obj.id, title).create()

    return await Image_Pydantic.from_tortoise_orm(image_obj)


@images_router.post("/{image_id}/like")
async def like(image_id: int, user: User = Depends(get_current_user)):
    image = await Image.get(id=image_id).prefetch_related("likes")

    if user in image.likes:
        await image.likes.remove(user)
        response = "unset"
    else:
        await image.likes.add(user)
        response = "set"

    return {"success": f"like has been {response}"}
