from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import json
import httpx
from urllib.parse import urlparse

from service.data_handler import create_log_data
from utility.request import get_config, get_logger, get_db_engine
from apistruct import RequestData


api_client = APIRouter()

templates = Jinja2Templates(directory="/mockapi/src/web/templates")


async def handle_json_data(request: Request) -> dict:
    try:
        json_data = await request.json()
    except json.JSONDecodeError:
        json_data = {}
    if request.method.upper() == "GET" and not json_data:
        json_data = dict(request.query_params)
    client_ip = request.client.host
    if isinstance(json_data, dict):
        target_url = json_data.get("target_url", str(request.url))
    else:
        target_url = str(request.url)
    method = request.method
    log_content = json.dumps(json_data, ensure_ascii=False)
    data_dict = {
        "client_ip": client_ip,
        "target_url": target_url,
        "method": method,
        "json_data": json_data,
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
    if request.method in ("GET", "HEAD"):
        # logger.debug(f"request method:{request.method}")
        # logger.debug(f"request query params:{request.query_params}")
        # logger.debug(f"path: {path}")
        if request.query_params:
            pass
        elif path:
            pass
        else:
            # 쿼리 파라미터 없이 루트 접근 -> main.html 렌더링
            # /main 함수로 리다이렉팅 하는 방법
            print(f"request query params:{request.query_params}")
            return templates.TemplateResponse("main.html", {"request": request})

    logger.debug(f"request header:{request.headers}")
    
    try:
        content_type = request.headers["Content-Type"]
        if "application/json" not in content_type:
            raise ValueError("Unsupported Media Type. Please use application/json.")
    except Exception as e:
        return JSONResponse(status_code=415, content={"error": str(e)})
    
    data: RequestData = await handle_json_data(request)
    use_json_param = True
    
    client_ip = data.client_ip
    target_url = data.target_url
    method = data.method
    json_data = data.json_data
    log_content = data.log_content
    
    if request.method in ("GET", "HEAD"):
        json_data = ""
        log_content = ""
    
    logger.info(f"요청 시작: 클라이언트 IP - {client_ip}, 메서드 - {method}")
    user_agent = request.headers.get("user-agent", "Unknown")

    target_url = await set_target_url(target_url, path, config)

    logger.debug(f"target url: {target_url}")
    logger.debug(f"content: {log_content}")

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
    except Exception as e:
        send_status = "FAIL"
        response_code = None
        error_message = str(e)
        logger.error(f"서버 전송 실패: {error_message}")
        server_response_data = {"error": error_message}
    
    if isinstance(server_response_data, dict):
        response_content = json.dumps(server_response_data, ensure_ascii=False)
    else:
        response_content = server_response_data
    
    log_data = create_log_data(
        config, logger, db_engine,
        method, user_agent, client_ip,
        request=log_content,
        response=response_content,
        send_status=send_status,
        response_code=response_code,
        error_message=error_message
    )
    logger.info(f"최종 로그 기록 완료: {log_data.method}, 상태: {log_data.send_status}")
    return JSONResponse(content=server_response_data)
