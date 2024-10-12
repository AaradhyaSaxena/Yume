import uuid
import os
import requests
from tqdm import tqdm
import numpy as np
from itertools import islice
from concurrent.futures import ThreadPoolExecutor, as_completed

import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document
from langchain.storage import LocalFileStore
from vertexai.vision_models import Image, MultiModalEmbeddingModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document
from langchain.storage import LocalFileStore
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate 

from vertexai.preview.generative_models import GenerativeModel, Image

class VectorStore:
    def __init__(self, pdf_path, user_id, persist_directory="./data/demo/health_book_data"):
        self.pdf_path = pdf_path
        self.user_id = user_id
        self.persist_directory = persist_directory
        self.vectorstore = Chroma(
            collection_name="health_data",
            embedding_function=HuggingFaceEmbeddings(),
            persist_directory=persist_directory
        )
        self.id_key = "doc_id"
        self.docstore = LocalFileStore(f"{self.persist_directory}/docstore")
        self.retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=self.docstore,
            id_key=self.id_key,
        )
        self.docstore = LocalFileStore(f"{self.persist_directory}/docstore")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.id_key = "doc_id"
        self.model = GenerativeModel("gemini-1.5-pro-001")
        os.makedirs(self.persist_directory, exist_ok=True)


    def load_pdf(self):
        loader = PyPDFLoader(self.pdf_path)
        pages = loader.load_and_split()
        texts = self.text_splitter.split_documents(pages)
        return texts

    def prepare_data(self):
        texts = self.load_pdf()
        doc_ids = [str(uuid.uuid4()) for _ in texts]
        summary_docs = [
            Document(
                page_content=doc.page_content,
                metadata={
                    self.id_key: doc_ids[i],
                    'source': doc.metadata.get('source', ''),
                    'page': doc.metadata.get('page', 0),
                    'user_id': self.user_id  # Associate the document with the user ID
                }
            )
            for i, doc in enumerate(texts)
        ]
        return doc_ids, [doc.page_content for doc in texts], summary_docs

 
    def add_to_stores(self):
            print("I am here")
            doc_ids, doc_contents, summary_docs = self.prepare_data()
            docstore_data = [
                (f"{self.user_id}_{doc_id}", doc_content.encode('utf-8'))  # Prefix doc_id with user_id
                for doc_id, doc_content in zip(doc_ids, doc_contents)
            ]
            for item in docstore_data:
                self.retriever.docstore.mset([item])
            for doc in tqdm(summary_docs, desc="Adding to Vectorstore"):
                self.retriever.vectorstore.add_documents([doc])


    def get_relevant_documents(self, query, limit=5):
        raw_docs = self.retriever.get_relevant_documents(query, limit=limit)
        
        decoded_docs = []
        for doc in raw_docs:
            # Check if the document belongs to the current user
            if isinstance(doc, Document) and doc.metadata.get('user_id') != self.user_id:
                continue  # Skip documents that do not belong to the user
            
            # Existing decoding logic
            if isinstance(doc, bytes):
                decoded_content = doc.decode('utf-8')
                decoded_doc = Document(page_content=decoded_content)
            elif isinstance(doc, Document):
                if isinstance(doc.page_content, bytes):
                    decoded_content = doc.page_content.decode('utf-8')
                    decoded_doc = Document(page_content=decoded_content, metadata=doc.metadata)
                else:
                    decoded_doc = doc
            else:
                continue
            
            decoded_docs.append(decoded_doc)
            
            if len(decoded_docs) >= limit:
                break
        print("retrieved docs ", decoded_docs)
        return decoded_docs
    
    def generate_answer(self, query, context):
        prompt = f"""Based on the following context from a health book or article, 
        please answer the question. If the answer cannot be directly inferred from the context, 
        use your general knowledge but prioritize the given information.
        
        Context:
        {context}
        
        Question: {query}

        Answer:"""

        response = self.model.generate_content(prompt)
        return response.text
    
    def query(self, user_query):
        relevant_docs = self.get_relevant_documents(user_query)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        answer = self.generate_answer(user_query, context)
        return answer