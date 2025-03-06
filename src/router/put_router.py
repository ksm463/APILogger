from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse


put_router = APIRouter()

@put_router.put("/update")
async def put_update_work(request: Request):
    body = await request.json()
    print(f"받은 요청: {body}")
    return JSONResponse(body)
