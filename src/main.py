from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import configparser
from router import get_router, post_router, put_router, delete_router


app = FastAPI()

app.mount("/static", StaticFiles(directory="/mockapi/src/web/static"), name="static")

config_path = "/mockapi/src/config.ini"
config = configparser.ConfigParser()
config.read(config_path)

app.state.config = config

timezone = config['ENV']['TIMEZONE']
csv_path = config['ENV']['CSV_PATH']


app.include_router(get_router)
app.include_router(post_router)
app.include_router(put_router)
app.include_router(delete_router)


if __name__== "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
