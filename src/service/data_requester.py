import httpx
import json
import logging
from typing import Any, Optional, Tuple


async def send_httpx_request(
    method: str,
    target_url: str,
    json_data: Any,
    use_json_param: bool,
    timeout: float = 10.0,
    logger: logging.Logger = None
) -> Tuple[str, Optional[int], Any, Optional[str]]:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if use_json_param:
                request_params = {"json": json_data}
            else:
                request_params = {"data": json_data}
            response = await client.request(method, target_url, **request_params)
        request_status = "SUCCESS"
        response_code = response.status_code
        error_message = None
        logger.info(f"server request succeeded: response code {response_code}")
        try:
            server_response_data = response.json()
        except json.JSONDecodeError:
            server_response_data = response.text
        return request_status, response_code, server_response_data, error_message
    except httpx.TimeoutException as e:
        request_status = "FAIL"
        response_code = None
        error_message = "The request timed out. You waited more than 10 seconds for a server response."
        logger.error(f"server request failed: {error_message}")
        server_response_data = {"error": error_message}
        return request_status, response_code, server_response_data, error_message
    except Exception as e:
        request_status = "FAIL"
        response_code = None
        error_message = str(e)
        logger.error(f"server request failed: {error_message}")
        server_response_data = {"error": error_message}
        return request_status, response_code, server_response_data, error_message
