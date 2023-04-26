from typing import Union
from pydantic import BaseModel


class QResource(BaseModel):

    uuid: Union[str, None] = None
    resource: Union[str, None] = None
    name: Union[int, None] = None
    total_quota: Union[int, None] = None
    used_quota: Union[int, None] = None

