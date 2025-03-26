import aiohttp
import json
import httpx
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


async def handle_json_data(request: Request) -> dict:
    try:
        json_data = await request.json()
    except json.JSONDecodeError:
        json_data = {}
    client_ip = request.client.host
    target_url = str(request.url)
    method = request.method
    log_content = json.dumps(json_data, ensure_ascii=False)
    return {
        "client_ip": client_ip,
        "target_url": target_url,
        "method": method,
        "json_data": json_data,
        "log_content": log_content
    }

async def handle_form_data(request: Request) -> dict:
    form = await request.form()
    client_ip = request.client.host
    target_url = form.get("ip", "")
    method = form.get("method", request.method)
    json_data = form.get("content", "")
    log_content = json_data
    return {
        "client_ip": client_ip,
        "target_url": target_url,
        "method": method,
        "json_data": json_data,
        "log_content": log_content
    }


@api_client.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(
    request: Request,
    path: str,
    config=Depends(get_config),
    logger=Depends(get_logger),
    db_engine=Depends(get_db_engine),
):
    """
    특별히 엔드포인트를 설정하지 않은 모든 요청을 받아오는 Catch-all API
    """
    content_type = request.headers.get("Content-Type", "")
    if "application/json" in content_type:
        data = await handle_json_data(request)
    else:
        data = await handle_form_data(request)
    
    client_ip = data["client_ip"]
    target_url = data["target_url"]
    method = data["method"]
    json_data = data["json_data"]
    log_content = data["log_content"]
    
    logger.info(f"[/send] 요청 시작: 클라이언트 IP - {client_ip}, 메서드 - {method}")
    user_agent = request.headers.get("user-agent", "Unknown")

    if not target_url:
        server_ip = config["ADDRESS"]["SERVER_IP_ADDRESS"]
        target_url = f"http://{server_ip}/{path}"
    # target_url = request.url
    print(f"target url:{target_url}")
    print(log_content)

    # httpx를 이용해 대상 서버에 요청 전송
    try:
        async with httpx.AsyncClient() as client:
            if isinstance(json_data, dict):
                request_params = {"json": json_data}
            else:
                request_params = {"data": json_data}
            response = await client.request(method, target_url, **request_params)
        send_status = "SUCCESS"
        response_code = response.status_code
        error_message = None
        logger.info(f"서버 전송 성공: 응답코드 {response_code}")
        try:
            server_response_data = response.json()
        except json.JSONDecodeError:
            server_response_data = response.text

    except Exception as exc:
        send_status = "FAIL"
        response_code = None
        error_message = str(exc)
        logger.error(f"서버 전송 실패: {error_message}")
        server_response_data = {"error": error_message}
    
    log_data = create_log_data(
        config, logger, db_engine,
        method, user_agent, client_ip,
        log_content,
        send_status=send_status,
        response_code=response_code,
        error_message=error_message
    )
    logger.info(f"최종 로그 기록 완료: {log_data.method}, 상태: {log_data.send_status}")
    return JSONResponse(content=server_response_data)
