import time
import json
from pathlib import Path
from app.redis_client import redis_client
from app.image_service import process_image

PROCESSED_DIR = Path("processed")
PROCESSED_DIR.mkdir(exist_ok=True)

print("worker started")

while True:
    task = redis_client.brpop("image_tasks")

    _,task_data = task

    task_data = json.loads(task_data)

    task_id = task_data["task_id"]
    input_path = task_data["input_path"]

    output_path = (
        PROCESSED_DIR /
        f"{task_id}.jpg"
    )

    redis_client.set(
        f"status:{task_id}",
        "processing"
    )

    try:

        process_image(
            input_path,
            str(output_path)
        )

        redis_client.set(
            f"status:{task_id}",
            "completed"
        )

        print(
            f"Completed: {task_id}"
        )

    except Exception as e:

        redis_client.set(
            f"status:{task_id}",
            "failed"
        )

        print(
            f"Failed: {task_id}"
        )

        print(e)
