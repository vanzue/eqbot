from fastapi import APIRouter

echo_space_router = APIRouter()


@echo_space_router.get("/echospace/ping")
async def ping_eqmaster():
    return "From echo space"
