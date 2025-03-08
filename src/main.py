from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, create_engine
import uvicorn
import configparser
from router import get_router, post_router, put_router, delete_router
from utility import setup_logger


app = FastAPI()

app.mount("/static", StaticFiles(directory="/mockapi/src/web/static"), name="static")

config_path = "/mockapi/src/config.ini"
config = configparser.ConfigParser()
config.read(config_path)

log_path = config['ENV']['LOG_PATH']
logger = setup_logger(log_path)
logger.info("Logging server started")
logger.info(f"config info : {log_path}")
# config에 들어온 값에 대한 로깅 필요(dict)
# 로그 파일 로테이션 필요

db_name = config['ENV']['DB_NAME']
DATABASE_URL = f"sqlite:////mockapi/src/database/{db_name}"
engine = create_engine(DATABASE_URL, echo=True)

app.state.config = config
app.state.logger = logger
app.state.engine = engine

app.include_router(get_router)
app.include_router(post_router)
app.include_router(put_router)
app.include_router(delete_router)

def create_db():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db()


if __name__== "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
