from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend URL if deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request model
class QueryRequest(BaseModel):
    input: str


# Define response endpoint
@app.get("/")
async def get_response(query: QueryRequest):
    response = agent_app.invoke({"input": query.input})
    return {"output": response["output"]}

# Run the FastAPI app (only if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
