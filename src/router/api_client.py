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
            json_data = form.get("content", "")
            log_content = json_data

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
                if response.status >= 400:
                    logger.error(f"요청 실패: 상태 코드 {response.status}, 응답 본문: {await response.text()}")
                    return JSONResponse(content={"error": f"서버 응답 오류 {response.status}"}, status_code=response.status)

                response_data = await response.json()
                logger.info(f"[/sendexample] 응답 수신 성공: 상태 코드 - {response.status}, 응답 데이터 - {response_data}")
                return JSONResponse(content=response_data, status_code=response.status)
    except Exception as e:
        logger.exception(f"예외 발생: {e}")
        return JSONResponse(content="서버 내부 오류", status_code=500)


@api_client.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(
    request: Request,
    path: str,
    config=Depends(get_config),
    logger=Depends(get_logger),
    db_engine=Depends(get_db_engine),
):
    """
    Catch-all API endpoint to handle any request.
    """
    client_ip = request.client.host
    method = request.method
    user_agent = request.headers.get("user-agent", "Unknown")
    headers = dict(request.headers)
    
    logger.info(f"Catch-all 메서드 요청 들어옴 : {method}, {user_agent}, {client_ip}, path: /{path}")

    try:
        body = await request.json()
    except json.JSONDecodeError:
        body = {}

    query_params = dict(request.query_params)

    request_info = {
        "method": method,
        "path": "/" + path,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "headers": headers,
        "body": body,
        "query_params": query_params,
    }

    log_data = create_log_data(
        config, logger, db_engine, method, user_agent, client_ip, str(request_info)
    )

    logger.info(f"받은 요청: {log_data.method}")
    return JSONResponse(content=request_info)
