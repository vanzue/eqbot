from fastapi import APIRouter

comic_router = APIRouter()


@comic_router.get("/comic/ping")
async def ping_eqmaster():
    return "From comic"
