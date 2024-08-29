from fastapi import APIRouter

router = APIRouter()


@router.get("/comic/ping")
async def ping_eqmaster():
    return "From comic"
