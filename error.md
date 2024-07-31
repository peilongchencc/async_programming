我使用的最新版python，我很迷惑 `asyncio.wait` 和 `asyncio.TaskGroup` 的区别和使用场景。

帮我查一下，我使用的最新版python，我很迷惑 `asyncio.wait` 和 `asyncio.TaskGroup` 的区别和使用场景。

帮我查一下，我使用的最新版python，当tasks是多个任务时，下列代码是只返回最快的那个任务的结果吗？那其他任务还运行吗？

```python
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
```


我使用的最新版python，请优化下列代码:

```python
import asyncio

async def coro1():
    await asyncio.sleep(1)
    print(f"任务1")
    return 'coro1 done'

async def coro2():
    await asyncio.sleep(2)
    print(f"任务2")
    return 'coro2 done'

async def coro3():
    await asyncio.sleep(3)
    print(f"任务3")
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
        for task in pending:
            task.cancel()
        
        print("Project have completed.")
        
        # 等待取消的任务完成
        await asyncio.wait(pending)

asyncio.run(main())
```
