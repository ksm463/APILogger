from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class APIRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, alias="index") # Index
    method: str                                # 요청 메서드 (GET, POST 등)
    user_agent: str                            # 요청 클라이언트 이름
    client_ip: str                             # 요청 IP
    content: str                               # 요청 내용
    time: datetime                             # 요청 시간
    send_status: Optional[str] = None          # 요청 성공/실패 상태 ('SUCCESS'/'FAIL' 등)
    response_code: Optional[int] = None        # 서버로부터 받은 응답 코드 (e.g. HTTP 200, 404 등)
    error_message: Optional[str] = None        # 실패했을 경우 에러 메시지

