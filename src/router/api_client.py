import aiohttp
import json
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from service.data_handler import create_log_data
from utility.request import get_config, get_logger, get_db_engine
from pathlib import Path
import logging

api_client = APIRouter()


@api_client.post("/send")
async def send_api_request(
    request: Request,
    config=Depends(get_config),
    logger: logging.Logger = Depends(get_logger),
    db_engine=Depends(get_db_engine),
    ip: str = Form(...),
    method: str = Form(...),
    content: str = Form(""),
):
    try:
        logger.info(f"[/send] 요청 시작: 서버 IP - {ip}, 메서드 - {method}")

        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")

        try:
            # 입력 값이 JSON 형식이면 파싱, 아니면 그대로 사용
            data = json.loads(content) if content.strip() else None
        except json.JSONDecodeError:
            data = content

        log_data = create_log_data(config, logger, db_engine, method, user_agent, client_ip, str(data))
        print(f"받은 요청: {log_data.method}")

        return JSONResponse(content="ok")
    except Exception as e:
        logger.exception(f"예외 발생: {e}")
        return JSONResponse(content="서버 내부 오류", status_code=500)
