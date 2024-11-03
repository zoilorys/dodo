from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, Form, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from qdrant_client.http.models import MatchValue, Filter, FieldCondition
from sqlmodel import select
from langchain_core.prompts import ChatPromptTemplate

from . import Document
from ..db import SessionDep
from ..templates import templates
from ..upload import upload_file

from ..vectorstore import vectorstore, DOCUMENT_COLLECTION_NAME, DOCUMENT_PAYLOAD_KEY
from ..llm import embeddings_llm, chat_llm

from ...celery.tasks import process_document


router = APIRouter()


@router.get("/")
def document_index(session: SessionDep, offset: int = 0, limit: int = 10):
    docs = session.exec(select(Document).offset(offset).limit(limit)).all()
    return docs


@router.get("/upload")
def document_upload(request: Request):
    return templates.TemplateResponse("document-upload.html", {
        "request": request,
        "title": "Upload"
    })


@router.get("/{document_id}")
def document_delete(session: SessionDep, document_id: str):
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return doc


@router.post("/")
async def document_create(
    session: SessionDep,
    filename: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    filepath = upload_file(filename, file)

    doc = Document(name=filename, path=filepath)

    session.add(doc)
    session.commit()
    session.refresh(doc)

    if doc.id is not None:
        process_document.delay(doc.id)

    return RedirectResponse(url="/documents", status_code=303)


@router.delete("/{document_id}")
def document_delete(session: SessionDep, document_id: int):
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    filepath = Path(doc.path)
    if filepath.exists() and filepath.is_file():
        filepath.unlink()

    vectorstore.delete(
        collection_name=DOCUMENT_COLLECTION_NAME,
        points_selector=Filter(
            must=FieldCondition(
                key=DOCUMENT_PAYLOAD_KEY,
                match=MatchValue(value=document_id)
            )
        )
    )

    session.delete(doc)
    session.commit()
    return Response(status_code=204)


@router.post("/process/{document_id}")
async def document_process(
        document_id: int
):
    process_document.delay(document_id)

    return { "ok": True }


@router.post("/query/{document_id}")
async def document_process(
        document_id: int,
        text: Annotated[str, Form()]
):
    system_prompt = """
    Answer user questions using provided context only.
    
    Below context is separated by dashes, so, please, do not mix the meaning together.
    Context:
    {context}
    """

    user_prompt = """
    {question}
    """

    query_vector = embeddings_llm.embed_query(text)

    search_result = vectorstore.query_points(
        collection_name=DOCUMENT_COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=FieldCondition(
                key=DOCUMENT_PAYLOAD_KEY,
                match=MatchValue(value=document_id)
            )
        ),
        with_payload=True,
        limit=3
    ).points

    context = "\n\n------------------------------\n\n".join([result.payload.get("content", "") for result in search_result])

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)
    ])

    request = prompt.format(question=text, context=context)

    response = chat_llm.invoke(request)

    return { "reply": response }
