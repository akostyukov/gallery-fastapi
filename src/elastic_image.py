from main import es


class ImageElastic:
    id: int
    image_link: str
    author: str

    def __init__(self, image_id, author_id, image_link):
        self.id = image_id
        self.image_link = image_link
        self.author = author_id

    async def create(self):
        await es.create("images", self.id, body={"image": self.image_link, "author": self.author})

    # @staticmethod
    # async def search():
    #     es.search(index="images")
