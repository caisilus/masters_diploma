from fastapi import FastAPI, UploadFile, File
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/webhook")
async def receive_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Читаем файл и сохраняем на диск
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    logger.info(f"Saved file: {file_path}")

    return {"status": "ok", "filename": file.filename}
