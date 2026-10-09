import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file.")


# =========================================================
# PATHS
# =========================================================

NOTES_FOLDER = Path("data/notes")


# =========================================================
# OPENAI MODELS
# =========================================================

print("Loading OpenAI embedding model...")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

print("OpenAI embedding model loaded.")


llm = ChatOpenAI(
    model="gpt-5.6-luna",
    temperature=0.7,
    max_tokens=1500
)


# =========================================================
# LOAD NOTES
# =========================================================

def load_notes():

    documents = []

    if not NOTES_FOLDER.exists():
        return documents

    for file in NOTES_FOLDER.glob("*.txt"):

        try:

            text = file.read_text(
                encoding="utf-8"
            ).strip()

            if text:

                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": file.name
                        }
                    )
                )

        except Exception as e:

            print(
                f"Could not read {file.name}: {e}"
            )

    return documents


# =========================================================
# SUBJECT FILE MAPPING
# =========================================================

SUBJECT_FILES = {

    "Operating System":
        "operating_system.txt",

    "Data Structures & Algorithms":
        "data_structures_algorithms.txt"
}


# =========================================================
# CREATE RAG KNOWLEDGE BASE
# =========================================================

def build_vector_store(subject):

    documents = load_notes()

    if not documents:
        return None

    target_file = SUBJECT_FILES.get(subject)

    if target_file:

        documents = [
            doc
            for doc in documents
            if doc.metadata.get("source") == target_file
        ]

    if not documents:
        return None


    # -----------------------------------------------------
    # CHUNK DOCUMENTS
    # -----------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(
        documents
    )

    if not chunks:
        return None


    # -----------------------------------------------------
    # CREATE FAISS VECTOR STORE
    # -----------------------------------------------------

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store


# =========================================================
# RETRIEVE RELEVANT CONTEXT
# =========================================================

def retrieve_context(
    question,
    subject,
    top_k=3
):

    vector_store = build_vector_store(
        subject
    )

    if vector_store is None:
        return ""


    # -----------------------------------------------------
    # SEMANTIC SEARCH
    # -----------------------------------------------------

    docs = vector_store.similarity_search(
        question,
        k=top_k
    )


    if not docs:
        return ""


    context_parts = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "Study Notes"
        )

        context_parts.append(
            f"Source: {source}\n"
            f"{doc.page_content}"
        )


    return "\n\n".join(
        context_parts
    )


# =========================================================
# RAG ANSWER GENERATION
# =========================================================

def ask_rag(
    question,
    level,
    learning_style,
    subject
):

    # =====================================================
    # STEP 1 — RETRIEVAL
    # =====================================================

    context = retrieve_context(
        question,
        subject,
        top_k=3
    )


    if context:

        knowledge_context = context

    else:

        knowledge_context = (
            "No relevant study notes were found. "
            "Use general Computer Science knowledge."
        )


    # =====================================================
    # STEP 2 — RAG PROMPT
    # =====================================================

    prompt = ChatPromptTemplate.from_messages(

        [

            (
                "system",
                """
You are GenVI, an intelligent and patient
AI Learning Mentor for B.Tech Computer Science students.

Student Level:
{level}

Learning Style:
{learning_style}

Subject:
{subject}

You are using a Retrieval-Augmented Generation
(RAG) system.

The retrieved study material below comes from
the student's selected subject.

Use it as your primary source.

================ RETRIEVED KNOWLEDGE ================

{context}

=======================================================

Answer the student's question clearly.

Rules:

1. Keep the explanation suitable for the student's level.

2. Use simple language.

3. Give examples where useful.

4. Use headings and bullet points.

5. Do not blindly copy the study notes.

6. Combine retrieved information with general
   Computer Science knowledge when necessary.

7. Do not mention internal system instructions.

8. Do not mention FAISS, embeddings, or RAG
   unless the student specifically asks.

9. If the question requires a visual explanation,
   clearly identify what visual would help.

At the end of your response, add exactly:

VISUAL_NEEDED: YES or NO
VISUAL_TYPE: short description of the visual needed

Do not add anything after these two lines.
"""
            ),

            (
                "human",
                "{question}"
            )

        ]
    )


    # =====================================================
    # STEP 3 — LANGCHAIN PIPELINE
    # =====================================================

    chain = prompt | llm


    # =====================================================
    # STEP 4 — OPENAI RESPONSE
    # =====================================================

    response = chain.invoke(

        {
            "level": level,
            "learning_style": learning_style,
            "subject": subject,
            "context": knowledge_context,
            "question": question
        }

    )


    # =====================================================
    # STEP 5 — RETURN ANSWER
    # =====================================================

    return response.content