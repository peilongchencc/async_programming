import asyncio

async def coro1():
    await asyncio.sleep(1)
    print("任务1")
    return 'coro1 done'

async def coro2():
    await asyncio.sleep(2)
    print("任务2")
    return 'coro2 done'

async def coro3():
    await asyncio.sleep(3)
    print("任务3")
    return 'coro3 done'

async def main():
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(coro1()),
            tg.create_task(coro2()),
            tg.create_task(coro3())
        ]

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # 获取第一个完成的任务的结果
        for task in done:
            print(f"First completed task result: {task.result()}")
        
        # 取消所有未完成的任务
        # for task in pending:
        #     task.cancel()

        print("Project has completed.")

asyncio.run(main())
