from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from service.data_handler import create_log_data
from database.data_manager import read_db
from utility.request import get_config, get_logger, get_db_engine


get_router = APIRouter()

templates = Jinja2Templates(directory="/mockapi/src/web/templates")


@get_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})


@get_router.get("/read")
async def get_latest_work(request: Request, logger = Depends(get_logger), db_engine = Depends(get_db_engine)):    
    
    client_ip = request.client.host
    method = request.method
    user_agent = request.headers.get("user-agent", "Unknown")

    logger.info(f"메서드 요청 들어옴 : {method}, {user_agent}, {client_ip}")

    log_data = read_db(logger, db_engine)

    logger.info("log data readed successfully")
    return JSONResponse(content=log_data)

@get_router.get("/list")
async def get_work_process(
    request: Request, 
    config = Depends(get_config), 
    logger = Depends(get_logger), 
    db_engine = Depends(get_db_engine), 
    param1: Optional[str] = Query(None),
    param2: Optional[int] = Query(None),

):
    client_ip = request.client.host
    method = request.method
    user_agent = request.headers.get("user-agent", "Unknown")

    logger.info(f"메서드 요청 들어옴 : {method}, {user_agent}, {client_ip}")
    
    body = {}

    if param1:
      body["param1"] = param1
    if param2:
      body["param2"] = param2

    log_data = create_log_data(config, logger, db_engine, method, user_agent, client_ip, str(body))

    logger.info(f"받은 요청: {log_data.method}")
    return JSONResponse(content=body)
