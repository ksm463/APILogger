from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.service.data_handler import create_log_data
from app.utility.request import get_config, get_logger, get_db_engine


post_router = APIRouter()

@post_router.post("/create")
async def post_add_work(request: Request, config = Depends(get_config), logger = Depends(get_logger), db_engine = Depends(get_db_engine)):
    client_ip = request.client.host
    method = request.method
    user_agent = request.headers.get("user-agent", "Unknown")

    logger.info(f"메서드 요청 들어옴 : {method}, {user_agent}, {client_ip}")

    body = await request.json()
    print(f"받은 내용: {body}")
    
    log_data = create_log_data(config, logger, db_engine, method, user_agent, client_ip, str(body))
    print(f"요청 메서드: {log_data.method}")

    message = "work added to AI server Successfully."

    return JSONResponse(content=message)
