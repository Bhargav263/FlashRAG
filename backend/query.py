from fastapi import APIRouter
from llm.llm import generate_response
from opik import track
from fastapi.responses import StreamingResponse

app = APIRouter()

@app.get("/chat")
async def chat(query: str):
    return StreamingResponse(generate_response(query), media_type="text/event-stream")

    # return {
    #     # "query": query,
    #     "answer": answer,
    #     # "retrieval_time": ret_time,
    #     # "generation_time": gen_time
    #     }