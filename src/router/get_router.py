from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates


get_router = APIRouter()

templates = Jinja2Templates(directory="/mockapi/src/web/templates")


@get_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})


@get_router.get("/read")
async def get_latest_work(request: Request):
    print(request)
    print(f"클라이언트 IP: {request.client.host}")
    print(f"요청 메서드: {request.method}")
    print(f"요청 URL: {request.url}")
    print(f"요청 헤더: {request.headers}")
    print(f"요청 상태: {request.state}")

    method = request.method
    body = await request.json()
    
    # log_data = create_log_data(method, body)

    print(f"받은 요청: {body}")
    return JSONResponse(content=body)

@get_router.get("/list")
async def get_work_process(request: Request):
    print(f"클라이언트 IP: {request.client.host}")
    print(f"요청 메서드: {request.method}")
    print(f"요청 URL: {request.url}")
    print(f"요청 헤더: {request.headers}")

    method = request.method
    body = await request.json()
    
    # log_data = create_log_data(method, body)

    print(f"받은 요청: {body}")
    return JSONResponse(content=body)
