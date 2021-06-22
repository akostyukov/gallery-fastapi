from typing import List

from fastapi import APIRouter, Depends

from auth import get_current_user
from models import Comment, Comment_Pydantic, CommentIn_Pydantic, User

comments_router = APIRouter(prefix="/images/{image_id}/comments", tags=["Comments"])


@comments_router.get("/", response_model=List[Comment_Pydantic])
async def get_comments(image_id: int):
    return await Comment_Pydantic.from_queryset(Comment.filter(image_id=image_id))


@comments_router.post("/", response_model=Comment_Pydantic)
async def create_comment(
    comment: CommentIn_Pydantic, image_id: int, user: User = Depends(get_current_user)
):
    comment_obj = await Comment.create(
        **comment.dict(exclude_unset=True), author_id=user.id, image_id=image_id
    )
    return await Comment_Pydantic.from_tortoise_orm(comment_obj)
