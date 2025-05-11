# APILogger

APILogger는 FastAPI를 사용하여 구축된 API 요청 로깅 및 프록시 서버 애플리케이션입니다. 들어오는 모든 API 요청과 해당 응답을 SQLite 데이터베이스에 기록하고, 특정 API 서버로 요청을 전달하는 프록시 기능을 제공합니다.

## 주요 기능

*   **API 요청/응답 로깅**:
    *   HTTP 요청(GET, POST, PUT, DELETE 등)의 상세 정보(시간, IP, User-Agent, 요청/응답 본문, 상태 코드 등)를 기록합니다.
    *   로그는 SQLite 데이터베이스에 저장됩니다.
*   **API 프록시 (Catch-all)**:
    *   정의되지 않은 경로로 들어오는 모든 요청을 지정된 대상 서버로 전달합니다.
    *   `Content-Type: application/json` 형식의 요청만 지원합니다.
*   **로그 조회**:
    *   저장된 로그를 API를 통해 조회할 수 있습니다 (최근 로그, 날짜별 조회).
*   **간단한 웹 인터페이스**:
    *   메인 페이지 및 입력 페이지를 제공합니다.

## 기술 스택

* **백엔드**: FastAPI, Uvicorn
* **데이터베이스**: SQLite, SQLModel
* **HTTP 클라이언트 (프록시용)**: httpx
* **Python 버전**: 3.10
* **패키지 관리**: uv
* **실행 환경**: Docker

## 프로젝트 구조

```
/APILogger
├── app/
│   ├── database/         # 데이터베이스 관련 모듈 (data_manager.py, SQLite DB 파일)
│   ├── router/           # API 라우터 (get_router.py, post_router.py, api_client.py 등)
│   ├── service/          # 비즈니스 로직 (data_handler.py, data_requester.py)
│   ├── utility/          # 유틸리티 모듈 (logger.py, request.py)
│   ├── web/              # 웹 관련 파일
│   │   ├── static/       # 정적 파일 (CSS, JS)
│   │   └── templates/    # HTML 템플릿
│   ├── apistruct.py      # API 데이터 구조 (Pydantic 모델, 예: RequestData)
│   └── config.ini        # 설정 파일
└── main.py               # FastAPI 애플리케이션 진입점
```

## Docker를 이용한 설치 및 실행

### 1. 사전 요구 사항

* Docker 가 설치되어 있어야 합니다.

### 2. Docker 이미지 빌드

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 Docker 이미지를 빌드합니다.
```bash
sh build_docker.sh
```

### 3. 설정

`/APILogger/app/config.ini` 파일을 환경에 맞게 수정합니다. 이 파일은 Docker 컨테이너 실행 시 호스트의 파일이 컨테이너 내부로 마운트되므로, 호스트에서 직접 수정하면 컨테이너에도 반영됩니다. 사용할 호스트와 서버의 주소를 정확히 설정하고 실행해 주세요.

**예시 `config.ini`**:

```ini
[ADDRESS]
CLIENT_IP_ADDRESS = 클라이언트 주소와 포트 (예: 192.168.123.106:3000)
SERVER_IP_ADDRESS = API 통신을 보낼 주소와 포트 (예: 192.168.219.106:8000)
LOCAL_IP_ADDRESS = APILogger 자체의 호스트 주소 
HOST = 0.0.0.0 
PORT = 8000 
```


### 4. Docker 컨테이너 실행

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 Docker 컨테이너를 시작합니다. app/config.ini 파일 수정 후 이 명령을 실행하십시오.

```bash
sh run_docker.sh
```

실행 후 아래의 명령어로 컨테이너에 접속하면 됩니다.

```bash
docker exec -it ksm_APILogger bash
```

### 5. 애플리케이션 실행(컨테이너 내부)
컨테이너 내부의 /APILogger 디렉토리에서 다음 명령어를 실행하여 FastAPI 애플리케이션을 시작합니다.

```bash
uv run main.py
```

애플리케이션이 시작된 후 호스트 머신의 웹 브라우저에서 config.ini의 LOCAL_IP_ADDRESS에 설정된 주소 (또는 http://localhost:<run_docker.sh에 설정된 포트>)로 접속할 수 있습니다. 예를 들어, run_docker.sh에서 port_num="1"로 설정했다면 http://localhost:18000 입니다.

## 웹 인터페이스 사용법

APILogger의 모든 주요 기능은 웹 브라우저를 통해 다음 페이지들에 접속하여 사용할 수 있습니다. APILogger 실행 후, 일반적으로 `http://localhost:<설정된 포트>` (예: `http://localhost:18000`) 주소로 접근합니다.

* **루트 페이지 (`/`)**:
    * 애플리케이션의 루트 주소로 접속하면 자동으로 아래의 "로그 조회 페이지 (`/main`)"로 이동합니다.
![Image](https://github.com/user-attachments/assets/c92f93bc-ecb0-4789-b121-6431bac08ede)

* **로그 조회 페이지 (`/main`)**:
    * **목적**: APILogger를 통해 기록된 모든 API 요청 및 응답 로그를 확인하는 페이지입니다. "API 통신 현황"이라는 제목으로 표시됩니다.
    * **화면 구성**:
        * 중앙에는 API 로그 목록이 테이블 형태로 표시됩니다. 각 로그 항목은 다음과 같은 정보를 포함합니다:
            * `Index`: 로그의 고유 번호
            * `Method`: 사용된 HTTP 메서드 (예: GET, POST)
            * `User-Agent`: 요청을 보낸 클라이언트 정보
            * `Client IP`: 요청 클라이언트의 IP 주소
            * `Request`: 전송된 요청의 주요 내용 (예: URL, 헤더, 본문 요약)
            * `Response`: 수신된 응답의 주요 내용 (예: 본문 요약)
            * `Time`: 요청이 기록된 시간
            * `Request Status`: 요청 처리 성공 여부 (예: SUCCESS, FAIL)
            * `Response Code`: 대상 서버로부터 받은 HTTP 상태 코드 (예: 200, 404)
            * `Error Message`: 요청 실패 시 발생한 에러 메시지
        * 테이블 하단에는 로그 조회 방식을 선택할 수 있는 버튼들이 있습니다.
    * **사용 방법**:
        * **최근 조회**: 페이지 로드 시 또는 "최근 조회" 버튼을 클릭하면 가장 최근에 기록된 API 로그들을 기본적으로 보여줍니다.
  ![Image](https://github.com/user-attachments/assets/44a74d30-702a-4d62-9d0b-c163ba698b7c)
        * **날짜별 조회**:
            1.  "날짜별 조회" 버튼을 클릭합니다.
            2.  화면에 나타나는 날짜 입력 필드에서 조회하고자 하는 "시작일"과 "종료일"을 선택합니다.
            3.  "조회" 버튼을 클릭하면 해당 기간 동안 기록된 로그들만 필터링하여 테이블에 표시합니다.
            4.  "취소" 버튼을 누르면 날짜 입력 필드가 사라집니다.

![Image](https://github.com/user-attachments/assets/e554e950-7f51-4bbf-ac3c-f825bb9c7b61)
* **API 요청 입력 페이지 (`/input`)**:
    * **목적**: 사용자가 직접 API 요청 정보를 입력하여 외부 서버로 전송하고, 그 과정과 결과를 APILogger에 기록(로깅)하기 위한 페이지입니다. "API 정보 입력 페이지"라는 제목으로 표시됩니다.
    * **화면 구성**:
        * API 요청 정보를 입력할 수 있는 폼(양식)이 제공됩니다.
    * **사용 방법**:
        1.  **IP (엔드포인트 주소)**: 드롭다운 목록에서 선택하거나 직접 입력란에 요청을 보낼 대상 서버의 전체 URL 주소를 입력합니다. (예: `http://your-target-api.com/data`)
        2.  **Method**: 드롭다운 목록에서 전송할 HTTP 메서드(POST, GET, DELETE, PUT 등)를 선택합니다.
        3.  **Content (본문 내용)**:
            * 텍스트 영역에 요청 시 함께 보낼 본문 데이터를 직접 입력합니다 (주로 JSON 형식).
            * 또는, "JSON 파일 업로드" 기능을 사용하여 로컬 컴퓨터에 있는 JSON 파일을 선택하여 본문 데이터로 첨부할 수 있습니다.
        4.  **반복 횟수**: 동일한 요청을 여러 번 반복해서 보내고 싶을 경우, 해당 횟수를 입력합니다. (기본값: 1)
        5.  **전송**: 모든 정보를 입력한 후 "전송" 버튼을 클릭합니다.
            * APILogger는 입력된 정보를 바탕으로 실제 대상 서버(`IP` 필드에 입력된 주소)에 API 요청을 수행합니다.
            * 이때의 요청 정보, 대상 서버로부터 받은 응답, 처리 상태 등 모든 과정이 APILogger 데이터베이스에 기록되며, "로그 조회 페이지 (`/main`)"에서 확인할 수 있습니다.
            * 이 페이지에서 "전송" 버튼을 누르면, 입력된 내용은 APILogger 자신의 프록시 기능(예: `http://localhost:18000` 과 같은 APILogger 주소의 특정 경로)을 통해 처리됩니다.

## 데이터베이스

APILogger를 통해 이루어지는 모든 API 요청과 응답의 상세 내용은 데이터베이스에 자동으로 기록됩니다. 사용자는 "웹 인터페이스 사용법"의 "로그 조회 페이지 (`/main`)"를 통해 이 기록된 내용을 확인할 수 있습니다.

* **저장 내용**: `main.html`의 로그 테이블에 표시되는 모든 정보(예: 고유 번호(Index), 요청 메서드, 클라이언트 정보, 요청/응답 내용, 시간, 처리 상태, 응답 코드, 에러 메시지 등)가 각 통신 건별로 저장됩니다.
* **저장 방식**:
    * 주요 데이터는 SQLite 데이터베이스 파일에 저장됩니다.
    * 데이터베이스 파일의 이름과 경로는 `app/config.ini` 파일의 `DB_NAME` 설정 (예: `api_log.db`)을 따르며, 일반적으로 `/APILogger/app/database/` 디렉토리 내에 생성됩니다.
    * 선택적으로, `app/config.ini` 파일의 `CSV_PATH` 설정에 따라 API 통신 기록이 CSV 파일 형태로도 저장될 수 있습니다.
* **데이터 관리**: 데이터베이스 파일은 Docker 볼륨 매핑을 통해 호스트 머신에서도 접근 및 유지가 가능하여, 컨테이너가 중지되거나 재시작되어도 기록이 보존됩니다.
