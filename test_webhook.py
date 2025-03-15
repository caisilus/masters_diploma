from fastapi import FastAPI, Request
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/webhook")
async def receive_file(request: Request):
    data = await request.form()
    file = data.get("file")
    if file:
        logger.info(f"GET FILE: {file.filename}")
    else:
        logger.error("ERROR: NO FILE")

    return {"status": "ok"}
