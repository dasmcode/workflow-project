from app.models.jobs import Job
from app.services.embedding_steps import search_similar
from app.core.openai_client import client
from app.services.cancel_service import check_cancel
from app.core.database import SessionLocal

def call_llm_with_context(user_prompt:str, system_prompt:str):
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    return response.choices[0].message.content.strip()

def query_rag(job:Job, query:str = ""):
    try:
        db = SessionLocal()
        if check_cancel(db, job):
            print(f"Job with id {job.id} has been cancelled")
            return False
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input = query
        )
        query_embedding = response.data[0].embedding
        if check_cancel(db, job):
            print(f"Job with id {job.id} has been cancelled")
            return False

        relevant_chunks = search_similar(job, query_embedding)
        if check_cancel(db, job):
            print(f"Job with id {job.id} has been cancelled")
            return False

        context = "\n".join(relevant_chunks)
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        system_prompt = "You are a helpful assistant that answers questions based on the provided context."
        answer = call_llm_with_context(prompt, system_prompt)
        return answer
    except Exception as e:
        print(f"Error during RAG query for job ID {job.id}: {str(e)}")
        return False


def query_summarize(job: Job, query: str = "Summarize this document", context: str = ""):
    try:
        db = SessionLocal()
        if check_cancel(db, job):
            print(f"Job with id {job.id} has been cancelled")
            return False
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        system_prompt = "You are a helpful assistant that answers questions based on the provided context."
        answer = call_llm_with_context(prompt, system_prompt)
        return answer
    except Exception as e:
        print(f"Error during summarize query for job ID {job.id}: {str(e)}")
        return False
