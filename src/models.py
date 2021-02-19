from tortoise import Tortoise, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class User(Model):
    email = fields.CharField(max_length=255, unique=True)
    username = fields.CharField(max_length=100)


class Comment(Model):
    author = fields.ForeignKeyField("models.User")
    text = fields.CharField(max_length=500)
    image = fields.ForeignKeyField("models.Image")


class Image(Model):
    image = fields.CharField(max_length=500)
    author = fields.ForeignKeyField("models.User")
    likes = fields.ManyToManyField("models.User", related_name="likes")


Tortoise.init_models(["models"], "models")

User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

Image_Pydantic = pydantic_model_creator(Image, name="Image")
ImageIn_Pydantic = pydantic_model_creator(Image, name="ImageIn", exclude_readonly=True)

Comment_Pydantic = pydantic_model_creator(Comment, name="Comment")
CommentIn_Pydantic = pydantic_model_creator(
    Comment, name="CommentIn", exclude_readonly=True, exclude=["author_id", "image_id"]
)
