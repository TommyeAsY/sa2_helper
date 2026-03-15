from rag.agent import load_full_knowledge


class KnowledgeIndex:
    def __init__(self, allowed_guilds: set[int]):
        self.allowed_guilds = allowed_guilds
        self.index = None

    async def load(self):
        self.index = await load_full_knowledge(self.allowed_guilds)

    def search(self, query: str):
        if self.index is None:
            return []
        return self.index.search(query)
