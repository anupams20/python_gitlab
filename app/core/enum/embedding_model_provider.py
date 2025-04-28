import enum


class EmbeddingModelProvider(str, enum.Enum):
    OPENAI = "ChatOpenAI"
    VERTEX_AI =  "ChatVertexAI"

