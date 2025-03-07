from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from service import create_log_data, read_csv
from utility import get_config


get_router = APIRouter()

templates = Jinja2Templates(directory="/mockapi/src/web/templates")


@get_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})


@get_router.get("/read")
async def get_latest_work(request: Request, config = Depends(get_config)):    
    
    client_ip = request.client.host
    method = request.method
    url = request.url
    headers = request.headers
    user_agent = request.headers.get("user-agent", "Unknown")

    print(f"request: {request}")
    print(f"클라이언트 IP: {client_ip}")
    print(f"요청 메서드: {method}")
    print(f"요청 URL: {url}")
    print(f"요청 헤더: {headers}")
    print(f"요청 상태: {request.state}")
    print(f"User-Agent: {user_agent}")
    
   
    log_data = read_csv(config)

    print("log data readed successfully")
    return JSONResponse(content=log_data)

@get_router.get("/list")
async def get_work_process(request: Request, config = Depends(get_config)):
    client_ip = request.client.host
    method = request.method
    url = request.url
    headers = request.headers
    user_agent = request.headers.get("user-agent", "Unknown")

    print(f"request: {request}")
    print(f"클라이언트 IP: {client_ip}")
    print(f"요청 메서드: {method}")
    print(f"요청 URL: {url}")
    print(f"요청 헤더: {headers}")
    print(f"요청 상태: {request.state}")
    print(f"User-Agent: {user_agent}")
    
    body = await request.json()
    
    log_data = create_log_data(config, method, user_agent, client_ip, content=str(body))

    print(f"받은 요청: {log_data.method}")
    return JSONResponse(content=body)
