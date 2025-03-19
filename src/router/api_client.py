import aiohttp
import json
from fastapi import APIRouter, Request, Depends
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
            client_ip = request.client.host
            target_url = request.url
            method_val = request.method
            json_data = await request.json()
            log_content = json.dumps(json_data, ensure_ascii=False)
            
        else:
            form = await request.form()
            client_ip = request.client.host
            target_url = form.get("ip")
            method_val = form.get("method")
            log_content = form.get("content", "")

        logger.info(f"[/send] 요청 시작: 클라이언트 IP - {client_ip}, 메서드 - {method_val}")

        user_agent = request.headers.get("user-agent", "Unknown")

        log_data = create_log_data(config, logger, db_engine, request.method, user_agent, client_ip, log_content)
        print(f"받은 요청: {log_data.method}")

        server_ip = config["ADDRESS"]["SERVER_IP_ADDRESS"]
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            logger.debug(f"[/sendexample] 서버로 POST 요청 전송 시도: URL - http://{server_ip}/testexample, 헤더 - {headers}, 데이터 - {log_content}")
            async with session.post(
                f"http://{server_ip}/testexample", headers=headers, json=json_data
            ) as response:
                logger.debug(f"[/sendexample] 서버로 POST 요청 전송: {server_ip}, 데이터 - {log_content}")
                response.raise_for_status()
                response_data = await response.json()
                logger.info(f"[/sendexample] 응답 수신 성공: 상태 코드 - {response.status}, 응답 데이터 - {response_data}")
                return JSONResponse(content=response_data, status_code=response.status)
    except Exception as e:
        logger.exception(f"예외 발생: {e}")
        return JSONResponse(content="서버 내부 오류", status_code=500)
