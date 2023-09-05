import threading

from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.vectorstore import VectorStore
from .routers import knowledgeqa

from app.config import Config
from app.models.llm import LLM
from app.models.embedding import EmbeddingModel
from app.models.search_image import SearchImageModel
from app.vectorstore import VectorStore
from app.embeddings.clip_embeddings import ClipEmbeddings
from app.deduplication import FileDeduplication


class GlobalObject:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def getInstance():
        return GlobalObject()._instance
    
    def __init__(self):
        self.config = Config()

        self.llm = LLM().load(config)
        self.embeddings = EmbeddingModel().load(config)

        self.vs_docs = VectorStore.create_with_chroma_docs(config=config, embeddings=self.embeddings)
        self.doc_qa = self.vs_docs.get_qa(llm=self.llm)

        self.search_image_model = SearchImageModel()
        self.search_image_model.load(config)

        self.clip_embeddings = ClipEmbeddings(self.search_image_model)
        self.vs_images = VectorStore.create_with_chroma_images(config=config, embeddings=self.clip_embeddings)

        self.file_deduplication = FileDeduplication(config)


global_object = None


config = Config()
app = FastAPI(title=config.TITLE, version=config.VERSION)
# app = FastAPI(title=config.TITLE, version=config.VERSION, 
#               docs_url=None, redoc_url=None)

app.include_router(knowledgeqa.router, prefix="/knowledgeqa", tags=["知识库问答"])


"""
env/lib/python3.10/site-packages/fastapi/openapi/docs.py
从上面的文件中可以找到如下文件：
    swagger-ui-bundle.js
    swagger-ui.css
    redoc.standalone.js
    favicon.png
"""

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# @app.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html():
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title=app.title + " - Swagger UI",
#         oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
#         swagger_js_url="/static/swagger-ui-bundle.js",
#         swagger_css_url="/static/swagger-ui.css",
#         swagger_favicon_url="/static/favicon.png",
#     )


# @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
# async def swagger_ui_redirect():
#     return get_swagger_ui_oauth2_redirect_html()


# @app.get("/redoc", include_in_schema=False)
# async def redoc_html():
#     return get_redoc_html(
#         openapi_url=app.openapi_url,
#         title=app.title + " - ReDoc",
#         redoc_js_url="/static/redoc.standalone.js",
#         redoc_favicon_url="/static/favicon.png",
#     )


# @app.get("/")
# async def index(request: Request):
#     # images = file.get_images('static/images/source')
#     return templates.TemplateResponse("index.html", 
#                                       {"request": request, "title": app.title, "version": app.version}) #, "images": images


import gradio as gr
from app.ui.webui import main as webui_main

# title = f'<h1>{app.title}</h1> <a href="docs">SwaggerUI</a> <a href="redoc">ReDoc</a>'
title = f'<h1>{app.title}</h1> <a href="docs" target="_blank">SwaggerUI</a> <a href="redoc" target="_blank">ReDoc</a>'
app = gr.mount_gradio_app(app, webui_main(title), path="/")


@app.on_event('startup')
def load_model():
    print('Startup GlobalObject')
    global global_object
    global_object = GlobalObject.getInstance()
