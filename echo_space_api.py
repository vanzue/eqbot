from fastapi import APIRouter

router = APIRouter()


@router.get("/echospace/ping")
async def ping_eqmaster():
    return "From echo space"
