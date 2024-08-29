from fastapi import APIRouter

eqmaster_router = APIRouter()


@eqmaster_router.get("/eqmaster/ping")
async def ping_eqmaster():
    return "From eq master"
