from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import json
import httpx
from urllib.parse import urlparse

from service.data_handler import create_log_data
from utility.request import get_config, get_logger, get_db_engine

api_client = APIRouter()


async def handle_json_data(request: Request) -> dict:
    try:
        json_data = await request.json()
    except json.JSONDecodeError:
        json_data = {}
    client_ip = request.client.host
    if isinstance(json_data, dict):
        target_url = json_data.get("target_url", str(request.url))
    else:
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
    print(f"request header:{request.headers}")
    
    if request.method in ["GET", "HEAD"]:
        query = request.query_params
        data = {
            "client_ip": request.client.host,
            # query string에 target_url 또는 ip 키를 확인
            "target_url": query.get("target_url") or query.get("ip") or str(request.url),
            "method": query.get("method", request.method),
            # json_data와 log_content는 query string에서 문자열로 전달됨
            "json_data": query.get("json_data", ""),
            "log_content": query.get("log_content", query.get("json_data", ""))
        }
        # GET/HEAD는 body 없이 처리하므로 use_json_param은 False
        use_json_param = False
    else:
        content_type = request.headers.get("Content-Type", "")
        if "application/json" in content_type:
            data = await handle_json_data(request)
            use_json_param = True
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            data = await handle_form_data(request)
            use_json_param = False
        else:
            # Content-Type이 명시되지 않은 경우 기본적으로 JSON 처리
            data = await handle_json_data(request)
            use_json_param = True
    
    client_ip = data["client_ip"]
    target_url = data["target_url"]
    method = data["method"]
    json_data = data["json_data"]
    log_content = data["log_content"]
    
    logger.info(f"요청 시작: 클라이언트 IP - {client_ip}, 메서드 - {method}")
    user_agent = request.headers.get("user-agent", "Unknown")

    local_address = config["ADDRESS"]["LOCAL_IP_ADDRESS"]
    parsed_url = urlparse(target_url)
    target_address = parsed_url.netloc
    if target_address == local_address:
        server_ip = config["ADDRESS"]["SERVER_IP_ADDRESS"]
        final_path = f"{path}" if path else parsed_url.path
        target_url = f"http://{server_ip}/{final_path}"

    print(f"target url: {target_url}")
    print(f"parsed url: {parsed_url}")
    print(f"target address: {target_address}")
    print(f"content:{log_content}")

    # httpx를 이용해 대상 서버에 요청 전송
    try:
        async with httpx.AsyncClient() as client:
            if use_json_param:
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
