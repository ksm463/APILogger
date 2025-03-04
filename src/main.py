from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
from router import get_router


app = FastAPI()

# 라우터 선언
get_router = APIRouter()
post_router = APIRouter()
put_router = APIRouter()
delete_router = APIRouter()

# app.mount("/static", StaticFiles(directory="/mockapi/src/web/static"), name="static")



@get_router.get("/read")
# 함수 선언부. API 통신 내용을 request를 이용해서 받아옴
async def get_latest_work(request: Request):
    # 받아온 json형태의 request를 꺼내서 body로 선언
    body = await request.json()
    # body의 내용을 print로 출력
    print(f"받은 요청: {body}")
    # 추후 DB에서 작업내용을 반환할 예정. 우선 body를 다시 반환함
    return body

@post_router.post("/create")
async def post_new_work(request: Request):
    body = await request.json()
    print(f"받은 요청: {body}")
    message = "work added to AI server Successfully."
    return message

@put_router.put("/update")
async def put_update_work(request: Request):
    body = await request.json()
    print(f"받은 요청: {body}")
    return body

@delete_router.delete("/delete")
async def delete_cancel_work(request: Request):
    body = await request.json()
    print(f"받은 요청: {body}")
    return body


app.include_router(get_router)
app.include_router(post_router)
app.include_router(put_router)
app.include_router(delete_router)


if __name__== "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)