import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings
from .schemas import DailyRates, DynamicRate, RangeParams, Rate
from .utils import make_dt_from_date

app = FastAPI()
db_client = AsyncIOMotorClient(settings.DATABASE_HOST, settings.DATABASE_PORT)


def get_db():
    return db_client[settings.DATABASE]


#@app.on_event("startup")
async def startup():

    db = get_db()
    d = datetime.datetime.today() - datetime.timedelta(days=2)
    document = {
        'created_at': make_dt_from_date(d.date()),
        'USD': Rate(value=70.31, code='USD', nominal=1, name='Доллар США').dict(),
        'EUR': Rate(value=83, code='EUR', nominal=1, name='Евро').dict()
    }
    await db.rates.insert_one(document)


@app.get('/dynamic', response_model=List[DynamicRate], summary='Currency dynamic')
async def dynamic(
        code: str,
        date_from: datetime.date = Query(..., alias='date-from'),
        date_to: datetime.date = Query(..., alias='date-to'),
        db=Depends(get_db)
) -> List[DynamicRate]:
    params = RangeParams(code=code, date_from=date_from, date_to=date_to)
    docs = await db.rates.find(**params.as_mongo_query()).to_list(None)
    return [DynamicRate.parse_from_docs(code, prev, curr) for prev, curr in zip(docs, docs[1:])]


@app.get('/archive', response_model=List[DailyRates], summary='Currency rates archive')
async def history(
        code: Optional[str] = None, date_from: Optional[datetime.date] = Query(None, alias='date-from'),
        date_to: Optional[datetime.date] = Query(None, alias='date-to'),
        db=Depends(get_db)
) -> List[DailyRates]:
    params = RangeParams(code=code, date_from=date_from, date_to=date_to)
    cursor = db.rates.find(**params.as_mongo_query())
    return [DailyRates.parse_from_doc(doc) for doc in await cursor.to_list(None)]


@app.get('/daily', response_model=DailyRates, summary='Daily currency rates')
async def daily_rates(
        code: Optional[str] = None, date: Optional[datetime.date] = Query(None, alias='date'), db=Depends(get_db)
) -> DailyRates:
    doc = await db.rates.find_one(**RangeParams(code=code, date_from=date, date_to=date).as_mongo_query())
    if doc is None:
        raise HTTPException(status_code=404, detail='Could`t find rates')
    return DailyRates.parse_from_doc(doc)
