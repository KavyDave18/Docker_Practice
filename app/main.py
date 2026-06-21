import json
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI,File,HTTPException,UploadFile
from fastapi.responses import FileResponse

from app.redis_client import redis_client

app = FastAPI(title="Image Compressor")

UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")

UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

@app.get("/")
def home():
    return{"messege":"Image Compressing Service"}


@app.post("/upload")
async def upload_image(file:UploadFile=File(...)):
    task_id = str(uuid.uuid4())

    file_path = (UPLOAD_DIR/f"{task_id}.jpg")

    with open(file_path,"wb")as buffer:
        shutil.copyfileobj(file.file,buffer)

        task = {
            "task_id":task_id,
            "input_path":str(file_path)
            }

        redis_client.set(f"status:{task_id}","queued")
        redis_client.lpush("image task",json.dumps(task))
        return{
            "task_id":task_id,
            "status":"queued"
        }

@app.get("/status/{task_id}")
def get_status(task_id:str):

    status = redis_client.get(f"status:{task_id}")

    if not status:
        raise HTTPException(status_code=404,detail="task not found")

    return{
        "task_id":task_id,
        "status":status
        }

@app.get("/download/{task_id}")
def download_image(task_id:str):
    output_file = (PROCESSED_DIR/f"{task_id}")

    if not output_file.exists():
        raise HTTPException(status_code=404,detail="Image Not Ready")

    return FileResponse(
        path=str(output_file),
        filename=f"{task_id}.jpg"
        )    


