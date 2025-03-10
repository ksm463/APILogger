from sqlmodel import Session, select
from datetime import datetime
from pathlib import Path
import pandas as pd
import logging
from apistruct import APIRequest


# # csv파일에서 index 번호를 읽어내는 함수. 추후 Db구현시 제거
# def get_next_index(csv_path: Path) -> int:
#     if not csv_path.exists():
#         return 1
#     with open(csv_path, "r", encoding="utf-8") as f:
#         line_count = sum(1 for _ in f)
#     return line_count if line_count > 0 else 1


# def write_contents_to_csv(logger: logging.Logger, log_entry: APIRequest, csv_path: Path) -> APIRequest:
#     # index 번호 산출
#     next_index = get_next_index(csv_path)
#     log_entry.index = next_index
#     logger.info(f"새 인덱스 번호 부여: {next_index}")
    
#     # APIRequestLog객체를 데이터프레임화
#     df_entry = pd.DataFrame([log_entry.dict()])
#     logger.debug("DataFrame created successfully")
    
#     df_entry.to_csv(
#         csv_path,
#         mode='a' if csv_path.exists() else 'w',
#         header=not csv_path.exists(),
#         index=False,
#         encoding='utf-8'
#     )
#     logger.info("CSV written successfully")
    
#     return log_entry

def write_contents_to_db(logger: logging.Logger, db_engine, log_entry: APIRequest) -> APIRequest:
    log_data = log_entry.model_dump()
    api_request_log = APIRequest(**log_data)
    
    with Session(db_engine) as session:
        session.add(api_request_log)
        session.commit()
        session.refresh(api_request_log)
        logger.info(f"새 인덱스 번호 부여: {api_request_log.id}")
        
    return api_request_log

def read_db(logger: logging.Logger, db_engine):
    try:
        with Session(db_engine) as session:
            statement = select(APIRequest)
            results = session.exec(statement).all()
            data = []
            for record in results:
                rec_dict = record.dict(by_alias=True)
                if isinstance(rec_dict["time"], datetime):
                    rec_dict["time"] = rec_dict["time"].strftime("%Y-%m-%d %H:%M:%S")
                data.append(rec_dict)
            logger.debug(f"DB 데이터 반환 완료: {data}")
            return data
    except Exception as e:
        logger.warning("DB 파일 읽기 실패:", e)
        return []
