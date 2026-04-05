from app.models.jobs import Job
from app.services.embedding_steps import search_similar
from app.core.openai_client import client

def query_rag(job:Job, query:str = "Summarize this document"):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input = query
    )
    query_embedding = response.data[0].embedding
    
    relevant_chunks = search_similar(query_embedding)

    context = "\n".join(relevant_chunks)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content.strip()