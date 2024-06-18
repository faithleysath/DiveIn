from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, List, Dict
from adapters.baidu.tiebaAPI import (
    fetch_thread_pn,
    fetch_posts_by_thread,
    fetch_comments_by_thread,
    get_like_forum,
    get_user_location,
    get_user_info,
    get_forum_thread,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime
import json


class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        def default_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()
            raise TypeError(
                f"Object of type {o.__class__.__name__} is not JSON serializable"
            )

        return json.dumps(
            content, default=default_converter, ensure_ascii=False
        ).encode("utf-8")


app = FastAPI()


@app.get("/api/forum/{forum_name}", response_model=Dict[str, Any])
def get_forum_info(forum_name: str, page: int = 1):
    try:
        forum_data, threads = get_forum_thread(forum_name, page)
        return CustomJSONResponse(
            content={"forum_data": forum_data, "threads": threads}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/thread/{thread_id}", response_model=List[Dict[str, Any]])
def get_thread_posts(thread_id: int):
    try:
        posts = fetch_posts_by_thread(thread_id)
        return CustomJSONResponse(content=posts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/comments/{thread_id}", response_model=List[Dict[str, Any]])
def get_thread_comments(thread_id: int):
    try:
        comments = fetch_comments_by_thread(thread_id)
        return CustomJSONResponse(content=comments)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/user/{portrait}", response_model=Dict[str, Any])
def get_user_info_by_portrait(portrait: str):
    try:
        user_info = get_user_info(portrait)
        return CustomJSONResponse(content=user_info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    app.mount("/", StaticFiles(directory="static"), name="static")
    uvicorn.run(app, host="0.0.0.0", port=8000)
