from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from service.data_handler import read_db_handler
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

    try:
        log_data = read_db_handler(logger, db_engine)
    except FileNotFoundError as e:
        # DB 파일이 없을 경우 에러 메시지를 JSON 형식으로 반환합니다.
        return JSONResponse(status_code=404, content={"error": str(e)})

    logger.info("log data readed successfully")
    return JSONResponse(content=log_data)

@get_router.get("/read/date")
async def get_db_by_date(
    request: Request,
    logger = Depends(get_logger),
    db_engine = Depends(get_db_engine),
    start_date: str = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="조회 종료일 (YYYY-MM-DD)")
):
    client_ip = request.client.host
    method = request.method
    user_agent = request.headers.get("user-agent", "Unknown")
    
    logger.info(f"메서드 요청 수신 : {method}, {user_agent}, {client_ip}")

    try:
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        logger.error("날짜 형식 오류: YYYY-MM-DD 형식으로 입력되어야 합니다.")
        return JSONResponse(status_code=400, content={"error": "날짜 형식은 YYYY-MM-DD 형식이어야 합니다."})

    try:
        log_data = read_db_handler(logger, db_engine, start_date_dt, end_date_dt)
    except FileNotFoundError as e:
        # DB 파일이 없을 경우 에러 메시지를 JSON 형식으로 반환합니다.
        return JSONResponse(status_code=404, content={"error": str(e)})

    logger.info("log data readed successfully")
    return JSONResponse(content=log_data)
