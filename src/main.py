from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, create_engine
import uvicorn
import configparser
from contextlib import asynccontextmanager
from pathlib import Path
from router import api_client, get_router, post_router, put_router, delete_router
from utility import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield
app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="/mockapi/src/web/static"), name="static")

config_path = "/mockapi/src/config.ini"
config = configparser.ConfigParser()
config.read(config_path)

log_path = config['ENV']['LOG_PATH']
logger = setup_logger(log_path)
logger.info("Logging server started")
logger.info(f"config info : {log_path}")

db_name = config['ENV']['DB_NAME']
db_dir = Path(__file__).parent / "database"
db_file_path = db_dir / db_name
DATABASE_URL = f"sqlite:///{db_file_path}"
logger.info(f"DB info : {db_file_path}")
db_engine = create_engine(DATABASE_URL, echo=False)

app.state.config = config
app.state.logger = logger
app.state.db_engine = db_engine

app.include_router(get_router)
app.include_router(post_router)
app.include_router(put_router)
app.include_router(delete_router)
app.include_router(api_client)

def create_db():
    SQLModel.metadata.create_all(db_engine)



if __name__== "__main__":
    host = config['ADDRESS']['HOST']
    port = config['ADDRESS']['PORT']
    uvicorn.run(app, host=host, port=int(port))
