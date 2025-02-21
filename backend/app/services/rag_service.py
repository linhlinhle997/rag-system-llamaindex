import hashlib
import json
import os
import shutil
from datetime import datetime

from app.db.models import UploadedFile
from dotenv import load_dotenv
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from sqlalchemy.orm import Session

load_dotenv()

# Retrieve necessary environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME")
DATA_PATH = os.getenv("DATA_PATH")
STORAGE_PATH = os.getenv("STORAGE_PATH")
METADATA_PATH = os.path.join(STORAGE_PATH, "processed_files.json")

# Initialize language and embedding models
llm = HuggingFaceInferenceAPI(model_name=LLM_MODEL_NAME, token=HF_TOKEN)
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)


def save_uploaded_file(file, db: Session):
    """
    Save an uploaded file to the specified data path and store its metadata in the database.
    """
    os.makedirs(DATA_PATH, exist_ok=True)
    file_path = os.path.join(DATA_PATH, file.filename)

    # Check if the file already exists in the database
    existing_file = db.query(UploadedFile).filter_by(filename=file.filename).first()
    if existing_file:
        return None

    # Save the uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store file metadata in the database
    db_file = UploadedFile(filename=file.filename, filepath=file_path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {"filename": file.filename, "path": file_path}


def delete_all_files(db: Session):
    """
    Delete all uploaded files from the system and clear database records.
    """
    files = db.query(UploadedFile).all()

    # Remove each file from disk if it exists
    for file in files:
        if os.path.exists(file.filepath):
            os.remove(file.filepath)

    # Remove file records from the database
    db.query(UploadedFile).delete()
    db.commit()

    # Remove the entire storage directory (if any files remain)
    shutil.rmtree(STORAGE_PATH, ignore_errors=True)
    return {"message": "All files deleted successfully"}


def save_processed_files(processed_files):
    """Save the list of processed files"""
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(processed_files, f)


def load_processed_files():
    """Load the list of processed files"""
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_existing_index():
    """Load the existing index if it exists"""
    if os.path.exists(os.path.join(STORAGE_PATH, "docstore.json")):
        print("Loading vector database from storage...")
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_PATH)
        index = load_index_from_storage(storage_context, embed_model=embed_model)

        processed_files = load_processed_files()

        print(f"Number of previously processed files: {len(processed_files)}")

        # for file_name, file_info in processed_files.items():
        #     print(f"   - {file_name} ({file_info.get('nodes_count', 0)} nodes)")
        return index, processed_files
    else:
        print("Vector database is empty, creating a new index!")
        return None, {}


def process_new_documents(documents, text_splitter, existing_index, processed_files):
    """
    Process new documents and update metadata
    """
    # Group documents by file name
    docs_by_filename = {}
    for doc in documents:
        file_path = doc.metadata.get("file_path", "")
        file_name = (
            os.path.basename(file_path)
            if file_path
            else doc.metadata.get("file_name", "unknown")
        )

        if file_name not in docs_by_filename:
            docs_by_filename[file_name] = []
        docs_by_filename[file_name].append(doc)

    # Process each file
    for file_name, file_docs in docs_by_filename.items():
        # Create nodes for the file
        combined_text = " ".join(doc.text for doc in file_docs)
        file_hash = hashlib.md5(combined_text.encode()).hexdigest()

        # Create nodes for the file
        all_nodes = []
        for doc in file_docs:
            nodes = text_splitter.get_nodes_from_documents([doc])
            # print(f"File {file_name}: created {len(nodes)} nodes")
            all_nodes.extend(nodes)

            # Add nodes to the index if available
            if existing_index:
                existing_index.insert_nodes(nodes)

        # Save processed file information
        processed_files[file_name] = {
            "hash": file_hash,
            "nodes_count": len(all_nodes),
            "last_processed": datetime.now().isoformat(),
        }


def query_rag(query_text: str, documents):
    """
    Perform a RAG query using stored documents.
    """

    os.makedirs(STORAGE_PATH, exist_ok=True)

    text_splitter = SentenceSplitter(chunk_size=2048, chunk_overlap=256)

    # Load or create the index
    index, processed_files = load_existing_index()

    print(
        f"Number of nodes in the database BEFORE adding: {len(index.docstore.docs) if index else 0}"
    )

    # If index does not exist, create a new one
    if index is None:
        print(f"Creating a new index from {len(documents)} documents...")
        # Create index and save metadata
        process_new_documents(documents, text_splitter, None, processed_files)
        index = VectorStoreIndex.from_documents(
            documents, transformations=[text_splitter], embed_model=embed_model
        )
        save_processed_files(processed_files)
        index.storage_context.persist(persist_dir=STORAGE_PATH)
    else:
        # Group documents by actual file name
        docs_by_file = {}
        for doc in documents:
            file_path = doc.metadata.get("file_path", "")
            if not file_path:
                file_path = doc.metadata.get("file_name", "unknown")

            if file_path not in docs_by_file:
                docs_by_file[file_path] = []
            docs_by_file[file_path].append(doc)

        # Check and process new or changed files
        new_or_changed_files = {}
        for file_path, file_docs in docs_by_file.items():
            file_name = os.path.basename(file_path)

            # Calculate hash for the combined content
            combined_text = " ".join(doc.text for doc in file_docs)
            current_hash = hashlib.md5(combined_text.encode()).hexdigest()

            # Detect new files
            if file_name not in processed_files:
                print(f"New file detected: {file_name}")
                new_or_changed_files[file_path] = file_docs
            # Detect changed files
            elif current_hash != processed_files[file_name].get("hash", ""):
                print(f"Changed file detected: {file_name}")
                new_or_changed_files[file_path] = file_docs

        if new_or_changed_files:
            # Process new or changed files
            all_new_docs = []
            for file_path, file_docs in new_or_changed_files.items():
                all_new_docs.extend(file_docs)

            print(
                f"Processing {len(all_new_docs)} documents from {len(new_or_changed_files)} new/changed files..."
            )

            # Process each file and update metadata
            process_new_documents(all_new_docs, text_splitter, index, processed_files)

            # Save processed files information
            save_processed_files(processed_files)
            if index:
                index.storage_context.persist(persist_dir=STORAGE_PATH)
        else:
            print("No new or changed files")
    print(f"Number of nodes in the database AFTER adding: {len(index.docstore.docs)}")

    # Initialize query
    retriever = index.as_retriever(similarity_top_k=10)
    response_synthesizer = get_response_synthesizer(llm=llm)

    class SortedRetrieverQueryEngine:
        """Query engine that sorts based on similarity score"""

        def __init__(self, retriever, response_synthesizer):
            self.retriever = retriever
            self.response_synthesizer = response_synthesizer

        def query(self, query):
            similarity_cutoff, max_selected_nodes = 0.5, 8
            nodes = [
                node
                for node in self.retriever.retrieve(query)
                if node.score >= similarity_cutoff
            ]
            return self.response_synthesizer.synthesize(
                query,
                sorted(nodes, key=lambda x: x.score, reverse=True)[:max_selected_nodes],
            )

    return SortedRetrieverQueryEngine(retriever, response_synthesizer).query(query_text)
