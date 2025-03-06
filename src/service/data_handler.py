from pathlib import Path
import pandas as pd
import arrow
from utility import APIRequestLog


def create_log_data(method: str, user_agent: str, client_ip: str, content: str) -> APIRequestLog:
    csv_path = Path("/mockapi/src/csv/api_logs.csv")

    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            if not df.empty and "index" in df.columns:
                next_index = int(df["index"].max()) + 1
            else:
                next_index = 1
        except Exception:
            next_index = 1
    else:
        next_index = 1
    
    print("csv loaded successfully")
    print(f"writing to nextindex: {next_index}")

    current_time = arrow.now('Asia/Seoul').format('YYYY-MM-DD HH:mm:ss')
    
    log_entry = APIRequestLog(
        index=next_index,
        method=method,
        user_agent=user_agent,
        client_ip=client_ip,
        content=content,
        time=current_time
    )

    df_entry = pd.DataFrame([log_entry.dict()])
    print("df_entry created successfully")

    df_entry.to_csv(
        csv_path,
        mode='a' if csv_path.exists() else 'w',
        header=not csv_path.exists(),  # 파일이 없으면 헤더 True, 있으면 False
        index=False,
        encoding='utf-8'
    )
    
    return log_entry
