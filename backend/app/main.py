from fastapi import FastAPI

app = FastAPI(title="NEZA AI Backend")

@app.get("/")
def root():
    return {"message": "NEZA AI Backend Running"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
