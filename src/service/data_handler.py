import arrow
import configparser
import logging
from typing import Optional, Any
from apistruct import APIRequest
from database.data_manager import write_contents_to_db



def create_log_data(
    config: configparser,
    logger: logging.Logger,
    db_engine,
    method: str,
    user_agent: str,
    client_ip: str,
    request: Any,
    response: Any,
    send_status: str = "PENDING",
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
        send_status=send_status,
        response_code=response_code,
        error_message=error_message
    )
    logger.info(f"APIRequestLog 객체 생성 완료: {method}, {client_ip}")

    log_entry = write_contents_to_db(logger, db_engine, log_entry)
    
    return log_entry
