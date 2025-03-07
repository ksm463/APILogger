from pydantic import BaseModel
from datetime import datetime

class APIRequest(BaseModel):
    index: int         # Index
    method: str        # 요청 메서드 (GET, POST 등)
    user_agent: str    # 요청 클라이언트 이름
    client_ip: str     # 요청 IP
    content: str       # 요청 내용
    time: datetime     # 요청 시간

