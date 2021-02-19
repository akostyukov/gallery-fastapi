from typing import List

from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import get_current_user
from main import app
from models import Comment, Comment_Pydantic, CommentIn_Pydantic


@app.get("/images/{image_id}/comments/", response_model=List[Comment_Pydantic])
async def get_comments(image_id: int):
    return await Comment_Pydantic.from_queryset(Comment.filter(image_id=image_id))


@app.post("/image/{image_id}/comments/", response_model=Comment_Pydantic)
async def create_comment(request: Request, comment: CommentIn_Pydantic, image_id: int):
    try:
        user = await get_current_user(request)
    except:
        return JSONResponse({"error": "user is not authenticated"})

    comment_obj = await Comment.create(
        **comment.dict(exclude_unset=True), author_id=user.id, image_id=image_id
    )
    return await Comment_Pydantic.from_tortoise_orm(comment_obj)
