from pathlib import Path
import pandas as pd
import arrow
import configparser
import logging
from apistruct import APIRequest
from database.data_manager import write_contents_to_db



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
