from fastapi import Request, HTTPException, status

def get_config(request: Request):
    try:
        config = request.app.state.config
        if config is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Config not initialized")
        return config
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Config attribute not found in app state")
