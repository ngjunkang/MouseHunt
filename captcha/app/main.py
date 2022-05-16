from fastapi import FastAPI, Response
from captcha_solver import solve_captcha
import uvicorn

app = FastAPI()

@app.get('/')
async def main(url: str):
    return Response(content=solve_captcha(url), media_type='text/plain')

if __name__ == '__main__':
    uvicorn.run("captcha.app.main:app", host="0.0.0.0", port=8080, reload=True, workers=2)
