from fastapi import APIRouter

router = APIRouter()


@router.get("/prove")
async def prove():
    return {"message": "Lean Server is running."}
