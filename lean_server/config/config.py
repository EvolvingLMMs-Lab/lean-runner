from pydantic import BaseModel


class LeanConfig(BaseModel):
    executable: str
    workspace: str


class SQLiteConfig(BaseModel):
    database_path: str
    timeout: int


class Config(BaseModel):
    lean: LeanConfig
    sqlite: SQLiteConfig
    logging: dict
