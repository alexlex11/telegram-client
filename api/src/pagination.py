from pydantic import BaseModel


def cur_num(offset: int, limit: int, obj: list) -> int:
    if offset + limit > len(obj):
        return offset + limit
    return len(obj)


class PaginationModel(BaseModel):
    current_count: int
    total_count: int
