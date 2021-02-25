from main import es
from models import User


class ImageElastic:
    id: int
    header: str
    link: str
    user: User

    def __init__(self):
        self.id = self.user.id
        self.header = self.user.name
        self.link = self.user.image

    async def create(self):
        await es.create("images", self.id, body={"header": self.header, "link": self.link})
