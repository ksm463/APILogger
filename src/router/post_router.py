from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse
from service import create_log_data


post_router = APIRouter()

@post_router.post("/create")
async def post_add_work(request: Request):
    client_ip = request.client.host
    method = request.method
    url = request.url
    headers = request.headers
    user_agent = request.headers.get("user-agent", "Unknown")

    print(f"request: {request}")
    print(f"클라이언트 IP: {client_ip}")
    print(f"요청 메서드: {method}")
    print(f"요청 URL: {url}")
    print(f"요청 헤더: {headers}")
    print(f"요청 상태: {request.state}")
    print(f"User-Agent: {user_agent}")

    body = await request.json()
    print(f"받은 요청: {body}")
    
    log_data = create_log_data(method, user_agent, client_ip, content=str(body))
    print(f"log data: {log_data}")

    message = "work added to AI server Successfully."

    return JSONResponse(content=message)
