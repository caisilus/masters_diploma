from fastapi import HTTPException, Header
import os

class APIKeyAuthenticator:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY not found in environment")

    def __call__(self, api_key: str = Header(None)):
        if not api_key:
            raise HTTPException(status_code=401, detail="Missing API Key header")

        if api_key != self.api_key:
            raise HTTPException(status_code=401, detail="Invalid API Key")

        return api_key
