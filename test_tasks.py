import asyncio

async def task(n):
    await asyncio.sleep(n)
    return n

async def main():
    tasks = [task(1), task(2), task(3)]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    
    print("Done tasks:")
    for task in done:
        print(await task)
    
    print("Pending tasks:")
    for task in pending:
        print(task)

asyncio.run(main())
