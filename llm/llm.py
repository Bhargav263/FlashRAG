import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from rag_pipeline.retrieve import retrieve
from dotenv import load_dotenv
from utils.logger import get_logger
import time
import asyncio
from opik import track

logger = get_logger("LLM")

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

async def generate_response(query):

    ret_start_time = time.time()
    docs = retrieve(query)
    retrieval_time = time.time() - ret_start_time

    context = "\n" .join([doc.page_content for doc in docs])

    logger.info(f"Retrieved {len(docs)} documents for query: {query}")
    print("=" *100)
    logger.info(f"Context :{context}")
    print("=" *100)
    system_prompt = ChatPromptTemplate.from_messages([
        (
            "system",

            """
            You are an halpful AI assistant, that helps user with their questions.Use this context to answer the question: {context}

            Use this "RULES": 
            -Always use polite tone.
            -Do not answer if the question is not related to the context.
            -If the question is not related to the context, answer that with polite tone and guide the user to the right path.
            -If user query is related to greetings answer those questions correctly.
            """
        
        ),

        ("human", "{query}")
    ])

    logger.info(f"System prompt created for query: {query}")

    try:
        llm = ChatGroq(
            api_key = api_key,
            model = "openai/gpt-oss-120b",
            temperature = 0.3,
            streaming = True
        )

        logger.info(f"LLM initialized for query: {query}")

        chain = system_prompt | llm

        start_time = time.time()
        import json

        async for chunk in chain.astream({"context": context,"query": query}):
            # Send the text content chunk to the client via SSE
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content})}\n\n"
            await asyncio.sleep(0)

        generation_time = time.time() - start_time
        
        # Send the final metrics chunk
        yield f"data: {json.dumps({'type': 'metrics', 'retrieval_time': retrieval_time, 'generation_time': generation_time})}\n\n"

    except Exception as e:
        raise Exception(f"Error generating response {e}")