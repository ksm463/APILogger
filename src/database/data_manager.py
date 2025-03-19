from sqlmodel import Session, select
from sqlalchemy import desc
from datetime import datetime
import logging
from apistruct import APIRequest


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
            statement = (
                select(APIRequest)
                .order_by(desc(APIRequest.id))
                .limit(10)
            )
            results = session.exec(statement).all()
            data = []
            for record in results:
                rec_dict = record.model_dump(by_alias=True)
                if isinstance(rec_dict["time"], datetime):
                    rec_dict["time"] = rec_dict["time"].strftime("%Y-%m-%d %H:%M:%S")
                data.append(rec_dict)
            logger.debug(f"DB 데이터 반환 완료: {data}")
            return data
    except Exception as e:
        logger.warning("DB 파일 읽기 실패:", e)
        return []
