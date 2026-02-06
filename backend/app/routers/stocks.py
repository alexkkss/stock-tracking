# 股票管理路由
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db, Stock
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

class StockCreate(BaseModel):
    code: str
    name: str

class StockResponse(BaseModel):
    code: str
    name: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[StockResponse])
def get_stocks(db: Session = Depends(get_db)):
    """获取所有股票"""
    stocks = db.query(Stock).all()
    return stocks

@router.post("/", response_model=StockResponse)
def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    """添加股票"""
    db_stock = db.query(Stock).filter(Stock.code == stock.code).first()
    if db_stock:
        raise HTTPException(status_code=400, detail="股票已存在")
    
    db_stock = Stock(code=stock.code, name=stock.name)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.delete("/{code}")
def delete_stock(code: str, db: Session = Depends(get_db)):
    """删除股票"""
    db_stock = db.query(Stock).filter(Stock.code == code).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    db.delete(db_stock)
    db.commit()
    return {"message": "删除成功"}
