"""
Author: peilongchencc@163.com
Description: 
模拟plan A和plan B,进行接口测试。
Requirements: 
Reference Link: 
Notes: 
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import random
import uvicorn

app = FastAPI()

class Item(BaseModel):
    key: str

@app.post("/api/companyA")
async def company_a(item: Item):
    # 模拟随机响应延时
    await asyncio.sleep(random.uniform(0.1, 0.5))
    # 模拟随机失败
    if random.choice([True, False]):
        return {"company": "A", "key": item.key, "status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Error in Company A API")

@app.post("/api/companyB")
async def company_b(item: Item):
    # 模拟随机响应延时
    await asyncio.sleep(random.uniform(0.1, 0.5))
    # 模拟随机失败
    if random.choice([True, False]):
        return {"company": "B", "key": item.key, "status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Error in Company B API")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
