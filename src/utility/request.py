from fastapi import Request, HTTPException, status

def get_config(request: Request):
    try:
        config = request.app.state.config
        if config is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Config not initialized")
        return config
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Config attribute not found in app state")

def get_logger(request: Request):
    try:
        logger = request.app.state.logger
        if logger is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logger not initialized")
        return logger
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logger attribute not found in app state")
