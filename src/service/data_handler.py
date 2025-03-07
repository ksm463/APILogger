from pathlib import Path
import pandas as pd
import arrow
from utility import APIRequest
from database import write_contents_to_csv



def create_log_data(method: str, user_agent: str, client_ip: str, content: str) -> APIRequest:
    current_time = arrow.now('Asia/Seoul').format('YYYY-MM-DD HH:mm:ss')
    
    log_entry = APIRequest(
        index=0,
        method=method,
        user_agent=user_agent,
        client_ip=client_ip,
        content=content,
        time=current_time
    )
    print("APIRequestLog 객체 생성 완료")
    
    csv_path = Path("/mockapi/src/database/api_logs.csv")    
    print("csv loaded successfully")


    log_entry = write_contents_to_csv(log_entry, csv_path)
    
    return log_entry


def read_csv():
    csv_path = Path("/mockapi/src/database/api_logs.csv")
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            data = df.to_dict(orient="records")
            return data
        except Exception as e:
            print("CSV 파일 읽기 실패:", e)
            return []
    else:
        print("CSV 파일이 존재하지 않습니다.")
        return []
