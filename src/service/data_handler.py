from pathlib import Path
import pandas as pd
import arrow
import configparser
import logging
from utility import APIRequest
from database import write_contents_to_db



def create_log_data(config: configparser, logger: logging.Logger, db_engine, method: str, user_agent: str, client_ip: str, content: str) -> APIRequest:
    timezone = config['ENV']['TIMEZONE']
    current_time = arrow.now(timezone).format('YYYY-MM-DD HH:mm:ss')
    
    log_entry = APIRequest(
        index=0,
        method=method,
        user_agent=user_agent,
        client_ip=client_ip,
        content=content,
        time=current_time
    )
    logger.info(f"APIRequestLog 객체 생성 완료: {method}, {client_ip}")

    log_entry = write_contents_to_db(logger, db_engine, log_entry)
    
    return log_entry


# def read_csv(config: configparser, logger: logging.Logger):
#     csv_path = Path(config['ENV']['CSV_PATH'])
#     logger.debug(f"CSV 파일 경로: {csv_path}")
#     if csv_path.exists():
#         try:
#             df = pd.read_csv(csv_path)
#             data = df.to_dict(orient="records")
#             logger.debug(f"데이터프레임 반환 완료: {data}")
#             return data
#         except Exception as e:
#             logger.warning("CSV 파일 읽기 실패:", e)
#             return []
#     else:
#         logger.warning("CSV 파일이 존재하지 않습니다.")
#         return []
