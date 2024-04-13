"""
Author: peilongchencc@163.com
Description: 
异步同时向2个接口发送内容,这2个接口的功能是一样的,只是不同的API,作用是plan A和plan B。只要其中一个有结果就返回那个结果,
另一个接口即使报错也没有关系。
Requirements: 
Reference Link: 
Notes: 
如果其中一个接口调用失败（比如报错），这个调用本身是被视为已完成的，因为 `asyncio.wait` 考虑的是任务的完成状态，
而不是成功或失败的结果。因此，即使某个接口调用失败，这也算是一个完成的任务，只是返回结果会是一个异常对象，你可以根据需要进行处理。
"""
import asyncio
import aiohttp

async def fetch(session, url, data):
    try:
        async with session.post(url, json=data) as response:
            return await response.json()  # 假设API返回JSON数据
    except Exception as e:
        return e  # 返回错误信息

async def fetch_first_complete(url1, url2, data):
    async with aiohttp.ClientSession() as session:
        task1 = asyncio.create_task(fetch(session, url1, data))
        task2 = asyncio.create_task(fetch(session, url2, data))
        
        done, pending = await asyncio.wait(
            [task1, task2], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task in pending:
            task.cancel()  # 取消还未完成的任务
        
        for task in done:
            return task.result()    # 获取完成的任务的结果。

# 假设的API URL和要发送的数据
url1 = "http://localhost:8000/api/companyA"
url2 = "http://localhost:8000/api/companyB"
# data = {"key": "value"}
data = {"key": "peilongchencc"}

# 运行函数
result = asyncio.run(fetch_first_complete(url1, url2, data))
print(result)