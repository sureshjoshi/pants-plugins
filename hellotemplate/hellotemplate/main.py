import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Template"}


def main():
    # Don't actually run FastAPI like this - it's just a PyOx proof-of-concept
    uvicorn.run(app, host="localhost", port=9000)


if __name__ == "__main__":
    print("Launching HelloTemplate from __main__")
    main()
