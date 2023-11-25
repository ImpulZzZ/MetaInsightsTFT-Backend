from routers import composition, composition_group, item, champion, trait

from fastapi import FastAPI

app = FastAPI()
app.include_router(composition.router)
app.include_router(composition_group.router)
app.include_router(item.router)
app.include_router(champion.router)
app.include_router(trait.router)