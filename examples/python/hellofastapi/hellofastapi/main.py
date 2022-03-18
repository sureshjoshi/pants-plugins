import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def main():
    # Don't actually run FastAPI like this - it's just a PyOx proof-of-concept
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    print("Launching HelloFastAPI from __main__")
    main()
