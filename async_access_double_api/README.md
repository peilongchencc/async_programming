# async access double api

模拟异步同时向2个接口发送内容，这2个接口的功能是一样的，只是不同的API，作用是plan A和plan B。只要其中一个有结果就返回那个结果，另一个接口即使报错也没有关系。<br>


## `return_first.py` 中代码解释:

```python
for task in pending:
    task.cancel()  # 取消还未完成的任务

for task in done:
    return task.result()
```

这段代码是用来处理异步任务完成后的情况。我们来逐步分析这两个循环的作用：<br>

1. **取消未完成的任务**：

```python
for task in pending:
    task.cancel()  # 取消还未完成的任务
```

在这里，`pending` 是一个集合，包含了那些在 `asyncio.wait` 函数中尚未完成的任务。<br>

当 `asyncio.wait` 使用 `return_when=asyncio.FIRST_COMPLETED` 参数时，它将在第一个任务完成时返回。这意味着可能还有其他任务正在执行或未完成。<br>

这个循环遍历所有未完成的任务，并对每一个执行 `cancel()` 方法，这个方法将取消任务的执行。取消任务是一个好的做法，可以避免无用的工作继续执行，尤其是在已经得到所需结果的情况下。<br>

2. **返回完成的任务的结果**：

```python
for task in done:
    return task.result()
```

`done` 集合包含了那些已经完成的任务。在这个场景中，笔者只关心第一个完成的任务，因为笔者想尽快得到结果。此循环迭代完成的任务，然后通过调用 `task.result()` 来获取任务的结果并返回它。<br>

由于使用的 `return_when=asyncio.FIRST_COMPLETED`，通常 `done` 集合中只有一个任务，这就是为什么这里可以直接在循环中返回结果。<br>

总结来说，这两段代码共同确保了一旦有一个任务成功完成，就立即取消其他所有还在进行中的任务，并且返回第一个完成的任务的结果。这样做可以有效地减少不必要的计算和网络资源的使用，特别是在只需要任何一个成功结果的情况下。<br>


‼️‼️‼️注意, 虽然现在 `done` 集合中只有一个任务, 但不可以使用 `done.result()` 获取任务的结果:<br>

在 Python 的 `asyncio` 库中，`done` 是一个集合（`set`），包含了所有已完成的任务。由于集合没有直接的 `.result()` 方法，你不能直接调用 `done.result()`。每个任务对象才有 `.result()` 方法，这用于获取该任务的返回值或抛出的异常。<br>

在处理异步任务时，你需要单独处理每个任务对象，以从中获取结果。如果你想获取第一个完成任务的结果，你可以使用这样的代码：<br>

```python
for task in done:
    return task.result()
```

这段代码逐个检查 `done` 集合中的任务，并返回第一个任务的结果。如果 `done` 中确实只有一个任务，这个循环就会在第一次迭代时返回那个任务的结果。<br>

如果你确信在你的代码逻辑中 `done` 集合中只有一个任务（即在`asyncio.wait`中设置为`return_when=asyncio.FIRST_COMPLETED`），也可以更简洁地写为：<br>

```python
return next(iter(done)).result()
```

这里使用 `iter()` 函数获取 `done` 集合的迭代器，`next()` 函数则从迭代器中取出第一个元素，即第一个完成的任务，然后调用其 `.result()` 方法来获取结果。<br>

以上两种方式都可以实现获取第一个完成的任务的结果，选择哪一种取决于你的具体需求和代码风格偏好。<br>