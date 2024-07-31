# import asyncio

# # 定义一个异步生成器
# async def async_generator():
#     for i in range(5):
#         await asyncio.sleep(1)
#         yield i

# # 定义一个协程来消费异步生成器
# async def consume_generator():
#     async for value in async_generator():
#         print(f"Received value: {value}")

# # 创建并运行任务
# async def main():
#     task = asyncio.create_task(consume_generator())
#     await task

# # 运行事件循环
# asyncio.run(main())

import asyncio

async def task1():
    for i in range(5):
        await asyncio.sleep(0.1)
        yield f"Task1 - Iteration {i}"

async def task2():
    for i in range(3):
        await asyncio.sleep(0.2)
        yield f"Task2 - Iteration {i}"

async def collect_results(agen):
    results = []
    async for result in agen:
        results.append(result)
    return results

async def main():
    # 创建任务
    t1 = task1()
    t2 = task2()
    
    # 同时运行两个任务
    results = await asyncio.gather(collect_results(t1), collect_results(t2))
    
    print("*"*10)
    print(results, type(results))
    print("*"*10)
    
    # 对结果进行一些处理
    for result in results:
        for item in result:
            print(item)
    
    return results

# 运行主函数
if __name__ == "__main__":
    results = asyncio.run(main())
    print(f"Both tasks completed with results: {results}")
