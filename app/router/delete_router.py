from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.service.data_handler import create_log_data
from app.utility.request import get_config, get_logger, get_db_engine


delete_router = APIRouter()

@delete_router.delete("/delete")
async def delete_cancel_work(request: Request, config = Depends(get_config), logger = Depends(get_logger), db_engine = Depends(get_db_engine)):
    client_ip = request.client.host
    method = request.method
    url = request.url
    headers = request.headers
    user_agent = request.headers.get("user-agent", "Unknown")

    logger.info(f"메서드 요청 들어옴 : {method}")
    print(f"request: {request}")
    print(f"클라이언트 IP: {client_ip}")
    print(f"요청 메서드: {method}")
    print(f"요청 URL: {url}")
    print(f"요청 헤더: {headers}")
    print(f"요청 상태: {request.state}")
    print(f"User-Agent: {user_agent}")
    
    body = await request.json()
    
    log_data = create_log_data(config, logger, db_engine, method, user_agent, client_ip, str(body))

    print(f"받은 요청: {log_data.method}")
    return JSONResponse(content=body)
