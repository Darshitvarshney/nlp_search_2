import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.routes.search import router 
from mongoengine import connect

load_dotenv()

app = FastAPI(
    title="WedPlanners NLP Search API",
    version="1.0.0",
    description="LLM + Rule Based NLP Search (Vendor & Venue, Read-Only)",
    docs_url="/docs"
)
DATABASE_NAME = os.getenv("DATABASE_NAME")
MONGODB_URI = os.getenv("MONGODB_URI")
connect(db=DATABASE_NAME, host=MONGODB_URI)

app.include_router(router, prefix="/api/v1")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)