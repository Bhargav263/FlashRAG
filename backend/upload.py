import os
from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from rag_pipeline.ingest import ingest
from utils.logger import get_logger
from opik import track

logger = get_logger("Upload")

app = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global metrics state
ingest_state = {
    "status": "idle",
    "metrics": {},
    "progress": 0,
    "message": ""
}

def update_progress(percent, message, metrics=None):
    global ingest_state
    ingest_state["progress"] = percent
    ingest_state["message"] = message
    if metrics is not None:
        ingest_state["metrics"].update(metrics)

def run_background_ingest(file_paths, strategy, chunk_size, chunk_overlap):

    logger.info(f"Starting background ingest for files: {file_paths}")
    global ingest_state
    ingest_state["status"] = "processing"
    ingest_state["metrics"] = {}
    ingest_state["progress"] = 0
    ingest_state["message"] = "Initializing..."
    try:
        metrics = ingest(file_paths, strategy, chunk_size, chunk_overlap, progress_callback=update_progress)
        ingest_state["metrics"] = metrics
        ingest_state["status"] = "done"
        ingest_state["progress"] = 100
        ingest_state["message"] = "✅ Knowledge base ready!"
    except Exception as e:
        ingest_state["status"] = "failed"
        ingest_state["metrics"] = {"error": str(e)}

@app.get("/metrics")
def get_metrics():
    return ingest_state


@app.post("/upload")
@track
async def upload_file(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    strategy: str = Form("Recursive Character"),
    chunk_size: int = Form(512),
    chunk_overlap: int = Form(64)
):
    file_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        file_paths.append(file_path)

    background_tasks.add_task(run_background_ingest, file_paths, strategy, chunk_size, chunk_overlap)
    
    logger.info(f"Files uploaded and background task started for files: {file_paths}")

    return {
        "status": "processing",
        "file_uploaded": len(file_paths)
    }