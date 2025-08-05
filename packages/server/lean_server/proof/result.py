from pydantic import BaseModel


class LeanProofResult(BaseModel):
    result: dict | None = None
    error_message: str | None = None
