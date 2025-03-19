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
):
    try:
        content_type = request.headers.get("Content-Type", "")
        if "application/json" in content_type:
            ip = request.client.host
            method_val = request.method
            json_data = await request.json()
            log_content = json.dumps(json_data, ensure_ascii=False)
            
            if isinstance(json_data, list):
                content_val = log_content
            elif isinstance(json_data, dict):
                content_val = json_data.get("content", "")
            else:
                content_val = ""
            
        else:
            form = await request.form()
            ip = form.get("ip")
            method_val = form.get("method")
            content_val = form.get("content", "")
            log_content = content_val
        
        # 필수 필드 검증
        if not ip or not method_val:
            raise ValueError("필수 필드가 누락되었습니다: ip와 method가 필요합니다.")

        logger.info(f"[/send] 요청 시작: 서버 IP - {ip}, 메서드 - {method_val}")

        user_agent = request.headers.get("user-agent", "Unknown")
        
        # 로그 데이터 생성 시 HTTP 메서드는 request.method 사용
        log_data = create_log_data(config, logger, db_engine, request.method, user_agent, ip, log_content)
        print(f"받은 요청: {log_data.method}")

        return JSONResponse(content=log_content)
    except Exception as e:
        logger.exception(f"예외 발생: {e}")
        return JSONResponse(content="서버 내부 오류", status_code=500)
