from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from pydantic import BaseModel
from pydantic import ValidationError

from app.utils import get_percent_change, make_dt_from_date


@dataclass
class RatesParams:
    code: Optional[str]

    def as_mongo_query(self) -> dict:
        query = {'sort': [('created_at', -1)]}
        if self.code:
            query['projection'] = {self.code: 1, 'created_at': -1}
        return query


@dataclass
class RangeParams:
    code: Optional[str]
    date_from: Optional[date]
    date_to: Optional[date]

    def _get_date_range_filter(self) -> Optional[dict]:
        query = defaultdict(dict)
        if self.date_from:
            query['created_at'].update({'$gte': make_dt_from_date(self.date_from)})
        if self.date_to:
            query['created_at'].update({'$lte': make_dt_from_date(self.date_to)})
        return query

    def as_mongo_query(self) -> dict:
        query = {'sort': [('created_at', -1)]}

        if self.code:
            query['projection'] = {self.code: 1, 'created_at': -1}

        dt_range_filter = self._get_date_range_filter()
        if dt_range_filter:
            query['filter'] = dt_range_filter

        return query


class Rate(BaseModel):
    value: float
    code: str
    nominal: int
    name: str


class DailyRates(BaseModel):
    date: date
    rates: List[Rate]

    @classmethod
    def parse_from_doc(cls, doc):
        rates = [v for k, v in doc.items() if k not in ('_id', 'created_at')]
        return DailyRates(date=doc['created_at'], rates=rates)


class DynamicRate(BaseModel):
    date: date
    value: float
    change: float

    @classmethod
    def parse_from_docs(cls, code: str, prev: dict, curr: dict) -> 'DynamicRate':
        try:
            return cls(
                date=curr['created_at'],
                value=curr[code]['value'],
                change=get_percent_change(prev[code]['value'], curr[code]['value'])
            )
        except KeyError:
            raise ValidationError()
