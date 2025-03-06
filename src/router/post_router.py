from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse


post_router = APIRouter()

@post_router.post("/create")
async def post_add_work(request: Request):
    print(f"요청 메서드: {request.method}")
    print(f"요청 URL: {request.url}")
    print(f"요청 헤더: {request.headers}")
    print(f"클라이언트 IP: {request.client.host}")

    body = await request.json()
    print(f"받은 요청: {body}")

    message = "work added to AI server Successfully."

    return JSONResponse(content=message)
