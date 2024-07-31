import asyncio

async def task(name, duration):
    print(f"Task {name} started, will take {duration} seconds.")
    await asyncio.sleep(duration)
    print(f"Task {name} completed.")
    return f"Result from {name}"

async def main():
    # 创建多个任务
    tasks = [
        asyncio.create_task(task("A", 2)),
        asyncio.create_task(task("B", 3)),
        asyncio.create_task(task("C", 1))
    ]
    
    # tasks = [task("A", 2), task("B", 3), task("C", 4)]
    
    # 使用 asyncio.wait 等待所有任务完成
    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    
    print("All tasks completed.")
    
    for d in done:
        print(f"Task result: {d.result()}")
        
# 运行事件循环
asyncio.run(main())
