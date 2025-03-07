from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from service import create_log_data
from utility import get_config


put_router = APIRouter()

@put_router.put("/update")
async def put_update_work(request: Request, config = Depends(get_config)):
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
