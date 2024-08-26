from fastapi import APIRouter

router = APIRouter()

@router.get("/eqmaster/ping")
async def ping_eqmaster():
    return "From eq master"