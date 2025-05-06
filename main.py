from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, create_engine
import uvicorn
import configparser
from contextlib import asynccontextmanager
from pathlib import Path
from app.router.get_router import get_router
from app.router.post_router import post_router
from app.router.put_router import put_router
from app.router.delete_router import delete_router
from app.router.api_client import catch_all_router
from app.utility.logger import setup_logger


config_path = "/APILogger/app/config.ini"
config = configparser.ConfigParser()
config.read(config_path)

db_name = config['ENV']['DB_NAME']
db_dir = Path(__file__).parent / "app" / "database"
db_file_path = db_dir / db_name
DATABASE_URL = f"sqlite:///{db_file_path}"
db_engine = create_engine(DATABASE_URL, echo=False)

def create_db():
    SQLModel.metadata.create_all(db_engine)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    log_path = config['ENV']['LOG_PATH']
    logger = setup_logger(log_path, logger_name="fastapi_app_logger") 
    
    app.state.config = config
    app.state.logger = logger
    app.state.db_engine = db_engine
    
    logger.info("Logging server started")
    logger.info(f"config info : {log_path}")
    logger.info(f"DB info : {db_file_path}")
    
    create_db()
    yield
    
    app.state.logger.info("Logging server stopped (from lifespan)")
    print("FastAPI application shutdown.")

app = FastAPI(lifespan=lifespan)

static_dir = Path("/mockapi/app/web/static")
app.mount("/web/static", StaticFiles(directory="/APILogger/app/web/static"), name="static")


app.include_router(get_router)
app.include_router(post_router)
app.include_router(put_router)
app.include_router(delete_router)
app.include_router(catch_all_router)


if __name__== "__main__":
    host = config['ADDRESS']['HOST']
    port = config['ADDRESS']['PORT']
    uvicorn.run("main:app", host=host, port=int(port), reload=True)
