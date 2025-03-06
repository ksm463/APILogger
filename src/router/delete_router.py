from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse


delete_router = APIRouter()

@delete_router.delete("/delete")
async def delete_cancel_work(request: Request):
    body = await request.json()
    print(f"받은 요청: {body}")
    return JSONResponse(body)
