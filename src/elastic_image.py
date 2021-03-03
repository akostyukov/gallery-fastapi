from main import es


class ImageElastic:
    id: int
    title: str

    def __init__(self, image_id, title):
        self.id = image_id
        self.title = title

    async def create(self):
        await es.create("images", self.id, body={"title": self.title})

    @staticmethod
    async def search(search_body: str):
        search_result = await es.search(
            index="images",
            body={
                "query": {
                    "query_string": {
                        "default_field": "title",
                        "query": f"{search_body}*",
                    }
                },
            },
        )

        list_of_id = [hit["_id"] for hit in search_result["hits"]["hits"]]
        return list_of_id
