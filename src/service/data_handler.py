from fastapi import Request
import json
import arrow
import configparser
import logging
from typing import Optional, Any
from urllib.parse import urlparse
from apistruct import APIRequest, RequestData
from database.data_manager import write_contents_to_db


async def handle_json_data(request: Request) -> dict:
    try:
        full_json = await request.json()
    except json.JSONDecodeError:
        full_json = {}

    if request.method.upper() == "GET" and not full_json:
        full_json = dict(request.query_params)

    client_ip = request.client.host
    if isinstance(full_json, dict):
        target_url = full_json.get("target_url", str(request.url))
    else:
        target_url = str(request.url)

    method = request.method
    if isinstance(full_json, dict) and "content" in full_json:
        payload = full_json["content"]
    # 없으면 기존 "json_data" 키 사용 (POSTMAN 등)
    elif isinstance(full_json, dict) and "json_data" in full_json:
        payload = full_json["json_data"]
    else:
        payload = full_json


    log_content = json.dumps(payload, ensure_ascii=False)
    data_dict = {
        "client_ip": client_ip,
        "target_url": target_url,
        "method": method,
        "json_data": payload,
        "log_content": log_content
    }
    return RequestData(**data_dict)


async def set_target_url(target_url: str, path: str, config: dict) -> str:
    print(f"target url: {target_url}")
    local_address = config["ADDRESS"]["LOCAL_IP_ADDRESS"]
    parsed_url = urlparse(target_url)
    target_address = parsed_url.netloc
    print(f"target address: {target_address}")
    if target_address == local_address:
        server_ip = config["ADDRESS"]["SERVER_IP_ADDRESS"]
        final_path = f"{path}" if path else parsed_url.path
        return f"http://{server_ip}/{final_path}"
    return target_url


def create_log_data(
    config: configparser,
    logger: logging.Logger,
    db_engine,
    method: str,
    user_agent: str,
    client_ip: str,
    request: Any,
    response: Any,
    request_status: str = "PENDING",
    response_code: Optional[int] = None,
    error_message: Optional[str] = None
) -> APIRequest:
    timezone = config['ENV']['TIMEZONE']
    current_time = arrow.now(timezone).format('YYYY-MM-DD HH:mm:ss')
    
    if not isinstance(request, str):
        request = str(request)
    if not isinstance(response, str):
        response = str(response)
    
    log_entry = APIRequest(
        index=0,
        method=method,
        user_agent=user_agent,
        client_ip=client_ip,
        request=request,
        response=response,
        time=current_time,
        request_status=request_status,
        response_code=response_code,
        error_message=error_message
    )
    logger.info(f"APIRequestLog 객체 생성 완료: {method}, {client_ip}")

    log_entry = write_contents_to_db(logger, db_engine, log_entry)
    
    return log_entry
