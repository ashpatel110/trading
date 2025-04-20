from pydantic import BaseModel


class OHLC(BaseModel):
    open: float
    high: float
    low: float
    close: float
