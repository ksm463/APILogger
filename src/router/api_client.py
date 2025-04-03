from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
import json

from service.data_handler import create_log_data, handle_json_data, set_target_url
from service.data_requester import send_httpx_request
from utility.request import get_config, get_logger, get_db_engine
from apistruct import RequestData


api_client = APIRouter()


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
            # 루트 엔드포인트로 접근 시 /main 함수로 리다이렉팅
            logger.debug(f"root endpoint called.")
            return RedirectResponse(url="/main")

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

    # httpx를 이용해 대상 서버에 요청 전송
    request_status, response_code, server_response_data, error_message = await send_httpx_request(
        method, 
        target_url, 
        json_data, 
        use_json_param, 
        timeout=10.0, 
        logger=logger
    )
    
    if isinstance(server_response_data, dict):
        response_content = json.dumps(server_response_data, ensure_ascii=False)
    else:
        response_content = server_response_data
    
    log_data = create_log_data(
        config, logger, db_engine,
        method, user_agent, client_ip,
        request=log_content,
        response=response_content,
        request_status=request_status,
        response_code=response_code,
        error_message=error_message
    )
    logger.info(f"최종 로그 기록 완료: {log_data.method}, 상태: {log_data.request_status}")
    return JSONResponse(content=server_response_data)
