import aiohttp
import json
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from service.data_handler import create_log_data
from utility.request import get_config, get_logger, get_db_engine
from pathlib import Path
import logging

api_client = APIRouter()


# @api_client.post("/send")
# async def send_api_request(
#     request: Request,
#     config=Depends(get_config),
#     logger: logging.Logger = Depends(get_logger),
#     db_engine=Depends(get_db_engine),
#     request_body: str = Query(..., description="JSON body as a string"),
# ):
#     server_ip = config["ADDRESS"]["SERVER_IP_ADDRESS"]
#     headers = {"Content-Type": "application/json"}
#     logger.info(f"[/send] 요청 시작: 서버 IP - {server_ip}, request_body - {request_body}")
#     try:
#         request_data = json.loads(request_body)
#         logger.debug(f"[/send] JSON 데이터 파싱 성공: {request_data}")
#     except json.JSONDecodeError as e:
#         logger.error(f"[/send] JSON 파싱 실패: {e}")
#         raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

#     try:
#         async with aiohttp.ClientSession() as session:
#             logger.debug(f"[/send] aiohttp ClientSession 시작")
#             async with session.post(
#                 f"http://{server_ip}", headers=headers, json=request_data
#             ) as response:
#                 logger.debug(
#                     f"[/send] 서버로 POST 요청 전송: {server_ip}, 데이터 - {request_data}"
#                 )
#                 response.raise_for_status()
#                 response_data = await response.json()
#                 logger.info(
#                     f"[/send] 응답 수신 성공: 상태 코드 - {response.status}, 응답 데이터 - {response_data}"
#                 )
#                 return JSONResponse(
#                     content=response_data, status_code=response.status
#                 )
#     except aiohttp.ClientError as e:
#         logger.error(f"[/send] aiohttp 클라이언트 오류: {e}")
#         raise HTTPException(status_code=500, detail=f"Request error: {e}")
#     except Exception as e:
#         logger.error(f"[/send] 예기치 않은 오류: {e}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@api_client.post("/sendexample")
async def send_api_request_example(
    request: Request,
    config=Depends(get_config),
    logger: logging.Logger = Depends(get_logger),
    db_engine=Depends(get_db_engine),
):
    server_ip = config["ADDRESS"]["SERVER_IP_ADDRESS"]
    example_file_path = Path(config['ENV']['TEMP_PATH'])
    headers = {"Content-Type": "application/json"}
    logger.info(f"[/sendexample] 요청 시작: 서버 IP - {server_ip}, 파일 경로 - {example_file_path}")

    if not example_file_path.exists():
        logger.error(f"[/sendexample] 예시 파일 없음: {example_file_path}")
        raise HTTPException(status_code=400, detail=f"example.json file does not exist: {example_file_path}")

    try:
        with open(example_file_path, "r") as request_body:
            request_data = json.load(request_body)
            logger.debug(f"[/sendexample] 파일 읽기 및 JSON 데이터 파싱 성공: {request_data}")

        async with aiohttp.ClientSession() as session:
            logger.debug(f"[/sendexample] 서버로 POST 요청 전송 시도: URL - http://{server_ip}/testexample, 헤더 - {headers}, 데이터 - {request_data}")
            async with session.post(
                f"http://{server_ip}/testexample", headers=headers, json=request_data
            ) as response:
                logger.debug(f"[/sendexample] 서버로 POST 요청 전송: {server_ip}, 데이터 - {request_data}")
                response.raise_for_status()
                response_data = await response.json()
                method = request.method
                user_agent = request.headers.get("User-Agent")
                client_ip = request.client.host
                log_data = create_log_data(config, logger, db_engine, method, user_agent, client_ip, str(request_data))
                logger.info(f"[/sendexample] 응답 수신 성공: 상태 코드 - {response.status}, 응답 데이터 - {log_data}")
                return JSONResponse(content=response_data, status_code=response.status)
    except aiohttp.ClientError as e:
        logger.error(f"[/sendexample] aiohttp 클라이언트 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"[/sendexample] JSON 파싱 실패: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except FileNotFoundError as e:
        logger.error(f"[/sendexample] FileNotFoundError: {e}")
        raise HTTPException(status_code=400, detail=f"example.json file cannot open. : {e}")
    except Exception as e:
        logger.error(f"[/sendexample] 예기치 않은 오류: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

