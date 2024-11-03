import logging
from io import StringIO

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from langchain_core.documents import Document as LCDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client.http.models import PointStruct

from src.dodo.db import get_session
from src.dodo.document import Document, DocumentStatus
from src.dodo.llm import embeddings_llm, EMBEDDING_CHUNK_SIZE, EMBEDDING_CHUNK_OVERLAP
from src.dodo.upload import load_file
from src.dodo.vectorstore import vectorstore, DOCUMENT_COLLECTION_NAME, \
    DOCUMENT_PAYLOAD_KEY

from .celery import celery


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery.task(name="process_pdf")
def process_document(document_id: int):
    logger.log(logging.INFO, "Document %d - starting processing", document_id)

    session = next(get_session())

    doc = session.get(Document, document_id)
    if not doc:
        logger.log(logging.INFO, "Document %d - not found", document_id)
        return

    logger.log(logging.INFO, "Document %d - found, processing...", document_id)

    doc.status = DocumentStatus.PROCESSING
    session.add(doc)
    session.commit()
    session.refresh(doc)

    file_io = load_file(doc.path)

    extracted_text_io = StringIO()
    extract_text_to_fp(file_io, extracted_text_io, laparams=LAParams(), output_type="text")
    extracted_text = extracted_text_io.getvalue()

    metadata = {DOCUMENT_PAYLOAD_KEY: document_id}
    lc_doc = LCDocument(
        page_content=extracted_text,
        metadata=metadata
    )

    logger.log(logging.INFO, "Document %d - extracted text..", document_id)

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=EMBEDDING_CHUNK_SIZE, chunk_overlap=EMBEDDING_CHUNK_OVERLAP
    )
    doc_splits = text_splitter.split_documents([lc_doc])

    logger.log(logging.INFO, "Document %d - text split...", document_id)

    vectors = embeddings_llm.embed_documents([d.page_content for d in doc_splits])

    logger.log(logging.INFO, "Document %d - pages embedded", document_id)

    points: list[PointStruct] = []
    for idx, pair in enumerate(zip(doc_splits, vectors)):

        logger.log(logging.INFO, "Document %d - embedding %d", document_id, len(pair[1]))

        points.append(
            PointStruct(
                id=document_id * 10000 + idx,
                vector=pair[1],
                payload={**metadata, "content": pair[0].page_content}
            )
        )

    vectorstore.upsert(
        collection_name=DOCUMENT_COLLECTION_NAME,
        points=points
    )

    logger.log(logging.INFO, "Document %d - processing done", document_id)

    doc.status = DocumentStatus.PROCESSED
    session.add(doc)
    session.commit()
