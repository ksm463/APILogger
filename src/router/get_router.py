from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from database.data_manager import read_db_latest
from utility.request import get_logger, get_db_engine


get_router = APIRouter()

templates = Jinja2Templates(directory="/mockapi/src/web/templates")


@get_router.get("/main", response_class=HTMLResponse)
async def read_root(request: Request, logger = Depends(get_logger)):
    logger.info(f"메인 페이지 로딩 요청 수신 : {request.method}")
    return templates.TemplateResponse("main.html", {"request": request})
  
@get_router.get("/input")
async def read_input_page(request: Request, logger = Depends(get_logger)):
    logger.info(f"입력 페이지 로딩 요청 수신 : {request.method}")
    return templates.TemplateResponse("input.html", {"request": request})


@get_router.get("/read")
async def get_latest_work(request: Request, logger = Depends(get_logger), db_engine = Depends(get_db_engine)):    
    
    client_ip = request.client.host
    method = request.method
    user_agent = request.headers.get("user-agent", "Unknown")

    logger.info(f"메서드 요청 수신 : {method}, {user_agent}, {client_ip}")

    log_data = read_db_latest(logger, db_engine)

    logger.info("log data readed successfully")
    return JSONResponse(content=log_data)

