from pydantic import BaseModel


class Metadata(BaseModel):
    source: str


class Document(BaseModel):
    content: str
    metadata: Metadata


class KnowledgeQA(BaseModel):
    content: str
    source_documents: list[Document]
