import datetime
from typing import Optional

from pydantic import BaseModel


class MyModel(BaseModel):
    date: Optional[datetime.date]


if __name__ == '__main__':
    m = MyModel(date='2020-08-16')
    print(m)
