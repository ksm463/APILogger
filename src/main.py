from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

app.state.config = config
app.state.logger = logger


app.include_router(get_router)
app.include_router(post_router)
app.include_router(put_router)
app.include_router(delete_router)


if __name__== "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
