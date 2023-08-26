import time
from fastapi import APIRouter
from app.base_model import KnowledgeQA, Document, Metadata

from app import main


router = APIRouter()


@router.post("/chat", summary="问答")
async def chat(prompt: str) -> KnowledgeQA:
    start_time = time.perf_counter()

    result = main.qa({"query": prompt})
    content = result["result"]

    documents = []
    for source_doc in result["source_documents"]:
        documents.append(Document(content=source_doc.page_content, 
                                  metadata=Metadata(source=source_doc.metadata["source"])))
    knowledgeqa = KnowledgeQA(content=content, source_documents=documents)

    predict_time = int((time.perf_counter() - start_time) * 1000)
    print(f'chat {prompt} {predict_time}ms')
    print(knowledgeqa)

    return knowledgeqa
