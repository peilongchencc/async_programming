# asyncio

本项目概述了用于 **"协程(coroutines)"** 和 **"任务(tasks)"** 的高级 asyncio APIs。<br>
- [asyncio](#asyncio)
  - [写法示例:](#写法示例)
    - [单 await 示例:](#单-await-示例)
    - [多个 await 示例:](#多个-await-示例)
  - [asyncio.create\_task():](#asynciocreate_task)
    - [使用set管理任务:](#使用set管理任务)
    - [强引用与弱引用:](#强引用与弱引用)
    - [拓展:集合的discard(element)方法](#拓展集合的discardelement方法)
    - [拓展:使用list管理任务](#拓展使用list管理任务)
  - [asyncio.TaskGroup:](#asynciotaskgroup)
  - [`.result()` 和 `await`的区别:](#result-和-await的区别)
    - [`.result()`示例代码:](#result示例代码)
    - [`await`示例代码:](#await示例代码)
    - [总结:](#总结)
  - [asyncio.gather](#asynciogather)
    - [基本用法](#基本用法)
    - [注意事项](#注意事项)
    - [示例：处理异常](#示例处理异常)
    - [示例2:展示同时计算的细节](#示例2展示同时计算的细节)
    - [示例2拓展:阶乘的计算方式](#示例2拓展阶乘的计算方式)
    - [示例3:`asyncio.create_task` 结合 `asyncio.gather`](#示例3asynciocreate_task-结合-asynciogather)
  - [`asyncio.gather`、`asyncio.create_task` 和 `asyncio.TaskGroup`:](#asynciogatherasynciocreate_task-和-asynciotaskgroup)
    - [总结:](#总结-1)
  - [asyncio.timeout](#asynciotimeout)
    - [使用示例:](#使用示例)
    - [使用场景](#使用场景)
    - [注意事项](#注意事项-1)
  - [asyncio.wait](#asynciowait)
    - [`asyncio.wait`函数签名:](#asynciowait函数签名)
    - [参数](#参数)
    - [返回值](#返回值)


## 写法示例:

### 单 await 示例:

例如，以下代码片段先打印“hello”，等待 1 秒钟，然后打印“world”：<br>

```python
import asyncio

async def main():
    print('hello')
    await asyncio.sleep(1)
    print('world')

asyncio.run(main())
```

终端输出:<br>

```log
hello
world
```

请注意: 不使用 `asyncio.run()`，直接调用 `main()` 会报错。<br>

### 多个 await 示例:

以下代码片段将在等待 1 秒后打印“hello”，然后在再等待 2 秒后打印“world”：<br>

```python
import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    print(f"started at {time.strftime('%X')}")

    await say_after(1, 'hello')
    await say_after(2, 'world')

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
```

终端输出如下:<br>

```log
started at 17:13:52
hello
world
finished at 17:13:55
```


## asyncio.create_task():

`asyncio.create_task()` 函数用于将协程作为 asyncio 任务 **并发运行** 。让我们修改上面的例子，并发运行两个 `say_after` 协程：<br>

> [!CAUTION]
> 异步是一种实现并发的方法，但并发不一定是异步的。例如，多线程和多进程也是实现并发的方式。

```python
import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    task1 = asyncio.create_task(
        say_after(1, 'hello'))

    task2 = asyncio.create_task(
        say_after(2, 'world'))

    print(f"started at {time.strftime('%X')}")

    # 等待两个任务都完成（大约需要2秒钟）。
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
```

终端输出如下:<br>

```log
started at 17:14:32
hello
world
finished at 17:14:34
```

🚨请注意，现在输出显示该代码片段比之前( **多个 await 示例** )快了1秒。<br>

### 使用set管理任务:

```python
import asyncio

# 定义一个示例协程函数
async def some_coro(param):
    await asyncio.sleep(3)  # 模拟异步操作
    print(f"Task with param {param} completed")

async def main():
    """
    - main 函数创建并启动了 10 个 some_coro 任务，并将每个任务添加到 background_tasks 集合中。
    - 每个任务在完成后会通过 add_done_callback 从 background_tasks 集合中删除自己。
    """
    background_tasks = set()

    for i in range(10):
        task = asyncio.create_task(some_coro(param=i))

        # 将任务添加到集合中。这会创建一个强引用。
        background_tasks.add(task)

        # 使用 add_done_callback 方法，为每个任务添加一个回调函数。在任务完成后，
        # 这个回调函数会从 background_tasks 集合中删除任务，从而避免集合无限增长，导致内存泄漏。
        task.add_done_callback(background_tasks.discard)

    # 等待所有任务完成
    await asyncio.gather(*background_tasks)

if __name__ == "__main__":
    asyncio.run(main())
```

> [!WARNING]
> 将任务添加到集合 (background_tasks) 中不会影响任务的执行顺序。虽然集合是无序的，但任务的创建和调度顺序由事件循环 (event loop) 控制，不受集合顺序的影响。

### 强引用与弱引用:

1. **没有赋值（弱引用）**：

当你创建任务而没有将其赋值给变量时，事件循环只保存对任务的弱引用。例如：<br>

```python
asyncio.create_task(some_coro(...))
```

在这种情况下，创建的任务没有被任何变量引用。如果没有其他地方引用这个任务，它可能会被垃圾回收机制回收，因为事件循环不会主动保留这些任务的强引用。<br>

2. **赋值（强引用）**：

当你创建任务并将其赋值给变量时，你创建了一个对任务的强引用。例如：<br>

```python
task1 = asyncio.create_task(some_coro(...))
task2 = asyncio.create_task(another_coro(...))
```

在这种情况下，`task1` 和 `task2` 变量持有这些任务的强引用。只要这些变量在作用域内存在并且未被覆盖，这些任务就不会被垃圾回收。<br>

### 拓展:集合的discard(element)方法

`background_tasks` 是一个集合（set），而 `background_tasks.discard` 是集合对象上的一个方法。它的作用是从集合中移除指定的元素。如果该元素不存在于集合中，`discard` 方法不会引发错误或异常，这一点与 `remove` 方法不同。<br>

```python
background_tasks = {"task1", "task2", "task3"}

# 使用 discard 移除一个元素
background_tasks.discard("task2")

print(background_tasks)
# 输出: {'task1', 'task3'}

# 使用 discard 移除一个不存在的元素，不会引发错误
background_tasks.discard("task4")

print(background_tasks)
# 输出: {'task1', 'task3'}
```

### 拓展:使用list管理任务

使用列表也是可以的，代码的逻辑不会改变。关键是跟踪所有创建的任务并等待它们完成。在这个例子中，set 和 list 都可以完成这个工作。

```python
import asyncio

# 定义一个示例协程函数
async def some_coro(param):
    await asyncio.sleep(3)
    print(f"Task with param {param} completed")

async def main():
    tasks = []

    for i in range(10):
        task = asyncio.create_task(some_coro(param=i))
        tasks.append(task)
        # 添加回调函数，任务完成后从列表中移除
        task.add_done_callback(tasks.remove)

    # 使用 asyncio.gather 等待所有任务完成
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
```

终端输出如下:<br>

```log
Task with param 0 completed
Task with param 1 completed
Task with param 2 completed
Task with param 3 completed
Task with param 4 completed
Task with param 5 completed
Task with param 6 completed
Task with param 7 completed
Task with param 8 completed
Task with param 9 completed
```


## asyncio.TaskGroup:

`asyncio.TaskGroup` 类提供了一种比 `create_task()` 更现代的替代方案。使用这个 API，`asyncio.create_task()` 中的示例变成了:<br>

```python
import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            say_after(1, 'hello'))

        task2 = tg.create_task(
            say_after(2, 'world'))

        print(f"started at {time.strftime('%X')}")

    # The await is implicit when the context manager exits.

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
```

> [!WARNING]
> `asyncio.TaskGroup` 和 `asyncio.create_task()` 的输出和耗时一致。


## `.result()` 和 `await`的区别:

### `.result()`示例代码:

```python
import asyncio

async def task1():
    print("Task 1 started")
    await asyncio.sleep(2)
    print("Task 1 completed")
    return "Result from task 1"

async def task2():
    print("Task 2 started")
    await asyncio.sleep(1)
    print("Task 2 completed")
    return "Result from task 2"

async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(task1())
        t2 = tg.create_task(task2())

    # 在 TaskGroup 结束后，我们可以获取任务的结果
    print(f"Task 1 result: {t1.result()}")
    print(f"Task 2 result: {t2.result()}")

asyncio.run(main())
```

### `await`示例代码:

```python
import asyncio

async def task1():
    print("Task 1 started")
    await asyncio.sleep(2)
    print("Task 1 completed")
    return "Result from task 1"

async def task2():
    print("Task 2 started")
    await asyncio.sleep(1)
    print("Task 2 completed")
    return "Result from task 2"

async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(task1())
        t2 = tg.create_task(task2())

    # 在 TaskGroup 结束后，我们可以获取任务的结果
    result1 = await t1
    result2 = await t2

    print(f"Task 1 result: {result1}")
    print(f"Task 2 result: {result2}")

asyncio.run(main())
```

### 总结:

在 `async with asyncio.TaskGroup() as tg:` 结束时，所有任务都已经完成，所以在这之后使用 `await t1` 和 `await t2` 实际上不会再等待什么，因为任务已经完成了。它们只是用于获取任务的结果。<br>

这样说来，确实没有必要在 `async with` 块结束后再使用 `await` 去等待任务完成，因为任务已经完成了。直接使用 `task.result()` 方法来获取结果会更简洁和直观。<br>

代码逻辑：<br>

1. `task1 = tg.create_task(task1())` 和 `task2 = tg.create_task(task2())` 创建并启动了两个任务。
2. 在 `async with asyncio.TaskGroup() as tg:` 块结束时，所有任务都已经完成。
3. 我们直接使用 `task1.result()` 和 `task2.result()` 获取任务的结果，而不需要再次 `await`。

这种方式更加简洁和直观，避免了不必要的 `await`。因此，使用 `result()` 方法在 `async with` 块结束后直接获取任务结果是更好的选择。<br>


## asyncio.gather

**`asyncio.gather` 是 Python `asyncio` 库中用于并行执行多个协程的函数。** 它能够同时运行多个异步任务并在所有任务完成后返回结果。以下是 `asyncio.gather` 的详细使用方法和注意事项。<br>

### 基本用法

```python
import asyncio

async def foo(x):
    await asyncio.sleep(x)
    return f"foo: {x}"

async def bar(y):
    await asyncio.sleep(y)
    return f"bar: {y}"

async def main():
    results = await asyncio.gather(
        foo(1),
        bar(2),
        foo(3)
    )
    print(results)

asyncio.run(main())
```

在上面的示例中，`foo` 和 `bar` 函数是两个异步任务。`asyncio.gather` 同时运行这些任务，并在它们全部完成后返回结果的列表。<br>

### 注意事项

1. **任务并行执行**：

- `asyncio.gather` 可以让多个协程并行执行，减少总的执行时间。例如，在上面的示例中，总的执行时间将是所有任务中最长的一个，而不是所有任务时间的总和。

2. **返回结果顺序**：

- `asyncio.gather` 返回一个结果列表，结果的顺序与传入 `gather` 中的协程顺序一致，而不是完成的顺序。

3. **异常处理**：

- 如果 `gather` 中的一个任务引发异常，默认情况下，`gather` 将立即引发此异常并取消所有剩余的任务(默认 `return_exceptions=False`)。可以通过传递 `return_exceptions=True` 参数让 `gather` 在返回结果列表时包含异常对象而不是引发它们。

```python
async def main():
    results = await asyncio.gather(
        foo(1),
        bar(2),
        foo(3),
        return_exceptions=True
    )
    print(results)
```

4. **取消任务**：

- 如果 `gather` 自身被取消，则所有收集到的协程也会被取消。

5. **性能注意事项**：

- 虽然 `asyncio.gather` 可以并行执行多个任务，但并不适用于 I/O 密集型操作（如文件读写、网络请求等）。对于这些场景，可以考虑使用 `concurrent.futures.ThreadPoolExecutor` 或 `concurrent.futures.ProcessPoolExecutor` 来实现真正的并行。

### 示例：处理异常

```python
import asyncio  # 引入异步编程模块 asyncio

# 定义一个异步函数 foo，接受一个参数 x
async def foo(x):
    await asyncio.sleep(x)  # 异步等待 x 秒
    return f"foo: {x}"  # 返回一个字符串，格式为 "foo: x"

# 定义另一个异步函数 bar，接受一个参数 y
async def bar(y):
    await asyncio.sleep(y)  # 异步等待 y 秒
    return f"bar: {y}"  # 返回一个字符串，格式为 "bar: y"

# 定义一个有错误的异步任务函数 faulty_task
async def faulty_task():
    await asyncio.sleep(1)  # 异步等待 1 秒
    raise ValueError("An error occurred")  # 抛出一个 ValueError 异常

# 定义主异步函数 main
async def main():
    try:
        # 使用 asyncio.gather 并行运行多个异步任务
        # return_exceptions=True 表示即使有任务抛出异常，也不会立即终止
        results = await asyncio.gather(
            foo(1),  # 执行 foo(1) 任务
            faulty_task(),  # 执行 faulty_task() 任务
            bar(2),  # 执行 bar(2) 任务
            return_exceptions=True  # 出现异常时返回异常而不是中断程序
        )
        
        print(results, type(results))  # 打印结果和结果的类型
        
        for result in results:  # 遍历每个结果
            if isinstance(result, Exception):  # 如果结果是异常
                print(f"Task raised an exception: {result}")  # 打印异常信息
            else:
                print(f"Task result: {result}")  # 打印任务返回的结果
    except Exception as e:  # 捕获所有其他异常
        print(f"Exception: {e}")  # 打印异常信息

asyncio.run(main())  # 运行主异步函数 main
```

终端输出如下:<br>

```log
['foo: 1', ValueError('An error occurred'), 'bar: 2'] <class 'list'>
Task result: foo: 1
Task raised an exception: An error occurred
Task result: bar: 2
```

在这个示例中，即使 `faulty_task` 引发了异常，`asyncio.gather` 也会返回所有任务的结果（包括异常对象），这样你可以在程序中处理它们。<br>

通过理解 `asyncio.gather` 的用法和注意事项，可以有效地并行执行多个异步任务，并在实际项目中合理应用这一强大的功能。<br>


### 示例2:展示同时计算的细节

```python
import asyncio

async def factorial(name, number):
    """计算num的阶乘"""
    f = 1   # 初始化阶乘结果为1
    for i in range(2, number + 1):
        print(f"任务 {name}: 计算({number})的阶乘, 当前 i={i}...")
        # 异步休眠1秒，以模拟计算过程中可能的等待时间
        await asyncio.sleep(1)
        # 更新阶乘结果
        f *= i
    print(f"任务 {name}: ({number})的阶乘 = {f}")
    return f

async def main():
    # 安排三次调用同时进行
    L = await asyncio.gather(
        factorial("A", 2),
        factorial("B", 3),
        factorial("C", 4),
    )
    print(L)

asyncio.run(main())
```

运行上述代码后，将依次显示下列内容，从输出中可以准确看到 **"同时运行"(并发)** 的效果:<br>

```log
任务 A: 计算(2)的阶乘, 当前 i=2...
任务 B: 计算(3)的阶乘, 当前 i=2...
任务 C: 计算(4)的阶乘, 当前 i=2...
```

```log
任务 A: (2)的阶乘 = 2
```

```log
任务 B: 计算(3)的阶乘, 当前 i=3...
任务 C: 计算(4)的阶乘, 当前 i=3...
```

```log
任务 B: (3)的阶乘 = 6
```

```log
任务 C: 计算(4)的阶乘, 当前 i=4...
```

```log
任务 C: (4)的阶乘 = 24
```

```log
[2, 6, 24]
```

### 示例2拓展:阶乘的计算方式

阶乘（Factorial）是对一个正整数n的所有正整数（包括n本身）相乘的结果，记作n!。<br>

2的阶乘是2，3的阶乘是6，4的阶乘是24。具体计算如下：<br>

2! = 2 x 1 = 2<br>

3! = 3 x 2 x 1 = 6<br>

4! = 4 x 3 x 2 x 1 = 24<br>

### 示例3:`asyncio.create_task` 结合 `asyncio.gather`

```python
import asyncio

# 定义一个异步协程函数 coro1
# 该函数会等待1秒钟，然后返回字符串 "Result 1"
async def coro1():
    await asyncio.sleep(1)
    return "Result 1"

# 定义另一个异步协程函数 coro2
# 该函数会等待2秒钟，然后返回字符串 "Result 2"
async def coro2():
    await asyncio.sleep(2)
    return "Result 2"

# 定义主异步函数 main
async def main():
    # 创建任务 task1，运行异步协程 coro1
    task1 = asyncio.create_task(coro1())
    # 创建任务 task2，运行异步协程 coro2
    task2 = asyncio.create_task(coro2())
    # 使用 asyncio.gather 等待所有任务完成，并将结果存储在 results 变量中
    results = await asyncio.gather(task1, task2)
    # 打印任务的结果
    print(f"Results: {results}")

# 使用 asyncio.run 运行主函数 main
asyncio.run(main())
```

等待2秒中后，终端输出如下:<br>

```log
Results: ['Result 1', 'Result 2']
```


## `asyncio.gather`、`asyncio.create_task` 和 `asyncio.TaskGroup`:

1. `asyncio.create_task`:

`asyncio.create_task` 创建并调度一个单独的任务，立即返回一个 `Task` 对象。这个对象可以在稍后进行操作或等待其完成。<br>

2. `asyncio.gather`:

`asyncio.gather` 是一种方便的方式，用于并行运行多个协程并收集它们的结果。它会等待所有传递的协程完成，并返回一个包含所有结果的列表。<br>

3. `asyncio.TaskGroup`:

`asyncio.TaskGroup` 是 Python 3.11 引入的一个新特性，用于更直观和灵活地管理一组任务。它提供了更清晰的任务管理和错误处理机制。<br>

### 总结:

这三种方式都能实现并行化，但 `asyncio.TaskGroup` 是最优选择，`asyncio.TaskGroup` 在许多情况下提供了更好的管理任务并行执行的方式，特别是在复杂任务管理和错误处理方面。<br>


## asyncio.timeout

在Python 3.11及其后续版本中，引入了一个新的异步上下文管理器`asyncio.timeout`，用于处理异步操作的超时。这个特性允许你更简洁地设置超时，并在超时发生时自动取消任务。<br>

### 使用示例:

```python
import asyncio

async def my_coroutine():
    print("Task started")
    await asyncio.sleep(5)  # 模拟一个耗时5秒的异步任务
    print("Task finished")

async def main():
    try:
        async with asyncio.timeout(3):  # 设置超时时间为3秒
            await my_coroutine()
    except asyncio.TimeoutError:
        print("The task took too long and was cancelled")

if __name__ == "__main__":
    asyncio.run(main())
```

终端输出如下:<br>

```log
Task started
The task took too long and was cancelled
```

> [!IMPORTANT]
> `asyncio.timeout()` 上下文管理器会将 `asyncio.CancelledError` 转换为 `TimeoutError`。

### 使用场景

1. **网络请求**：在执行可能长时间等待的网络请求时，可以使用超时来防止程序挂起。

2. **并发任务**：在并发任务中，避免单个任务的长时间运行影响整体进度。

3. **资源获取**：在获取外部资源（如数据库连接）时，设置超时来确保资源及时释放。

### 注意事项

- `asyncio.timeout` 只能用于异步上下文中。

- 它在超时发生时会取消当前任务，这意味着如果你有多个并发任务，需要确保它们的取消处理是安全的。

这个新特性使得处理异步超时更加简洁和直观，相比于以前使用`asyncio.wait_for`的方式，有了更好的代码可读性和维护性。<br>


## asyncio.wait

`asyncio.wait` 用于协同多个异步操作，它允许您等待一个或多个协程完成，并可以指定完成的条件（例如，所有协程都完成，或任意一个协程完成）。<br>

### `asyncio.wait`函数签名:

```bash
asyncio.wait(aws, *, timeout=None, return_when=ALL_COMPLETED)
```

> [!CAUTION]
> asyncio.wait 只是确保在至少一个任务完成时返回，而不会取消其他未完成的任务。为避免程序延迟退出，需要取消其他任务。


### 参数

- **`aws(awaitables)`**: 任务的集合或列表（python 3.11后禁止传递协程），这些任务集合/列表将在 `asyncio.wait` 中被等待完成。

- **`timeout`** (可选): 超时时间（以秒为单位）。如果设置了超时，`asyncio.wait` 将在指定时间内返回，即使一些任务尚未完成。

- **`return_when`** (可选): 指定函数何时返回。可以是以下常量之一：
  - `asyncio.ALL_COMPLETED`: 所有任务完成时返回（默认值）。
  - `asyncio.FIRST_COMPLETED`: 任意一个任务完成时返回。
  - `asyncio.FIRST_EXCEPTION`: 任意一个任务抛出异常时返回。

### 返回值

- 返回一个元组 `(done, pending)`，其中：
  - `done` 是已完成的任务的集合。
  - `pending` 是尚未完成的任务的集合。
