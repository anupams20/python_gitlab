import enum


class LLMProviderEnum(str, enum.Enum):
    OPENAI = "ChatOpenAI"
    VERTEX_AI = "ChatVertexAI"
