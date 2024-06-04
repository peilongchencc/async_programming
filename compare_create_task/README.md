# "依次调用异步函数"和"并行执行任务" 效果对比

时常纠结，当自己的函数是异步函数时，常规"依次调用异步函数"和"并行执行任务"好像效果差不多，这里就测试一下。<br>

> 通过添加一些人工的延迟（如 `await asyncio.sleep`），方便更明显地看到并行执行的效果。

## 依次调用异步函数代码:

```python
import os
import asyncio
from loguru import logger
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv("env_config/.env.local")

# 创建openai客户端
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_openai_response_unstream(chat_history, task_name):
    """根据历史聊天数据与llm交互,返回结果以非流式输出。
    """
    logger.info(f"Task {task_name} started")
    await asyncio.sleep(3)  # 模拟网络请求延迟
    completion = await client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model=os.getenv('CHAT_MODEL'),
        messages=chat_history,
        # stream=True
    )
    logger.info(f"Task {task_name} completed")
    return completion.choices[0].message.content

async def main():
    chat_history1 = [{"role": "user", "content": "Tell me a joke."}]
    chat_history2 = [{"role": "user", "content": "Explain quantum computing in simple terms."}]

    # 依次调用异步函数
    response1 = await get_openai_response_unstream(chat_history1, "Task 1")
    response2 = await get_openai_response_unstream(chat_history2, "Task 2")

    # 处理结果
    logger.info(f"Response 1: {response1}")
    logger.info(f"Response 2: {response2}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 终端显示:

```log
(langchain) root@iZ2zea5v77oawjy2qz7c20Z:/data/bank_chatbot# python tests/test_create_mul_tasks_log_test1.py 
2024-06-04 13:50:21.636 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 1 started
2024-06-04 13:50:25.706 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 1 completed
2024-06-04 13:50:25.706 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 2 started
2024-06-04 13:50:33.501 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 2 completed
2024-06-04 13:50:33.501 | INFO     | __main__:main:62 - Response 1: Sure, here's a light-hearted joke for you:

Why don't scientists trust atoms?

Because they make up everything!
2024-06-04 13:50:33.501 | INFO     | __main__:main:63 - Response 2: Sure! Let's imagine you have a really, really powerful calculator. Traditional computers, like the one you might be using right now, work a bit like super-fast calculators. They process information using something called bits, which can be in one of two states: 0 or 1. Think of these like tiny switches that are either off (0) or on (1).

Quantum computers, on the other hand, use something called **qubits**. Unlike regular bits, qubits can be both 0 and 1 at the same time. This is due to a property of quantum physics called superposition. Imagine you have a spinning coin that is both heads and tails until it lands. That's kind of what a qubit is like.

But there's more! Qubits can also be entangled, a special connection that means the state of one qubit can depend on the state of another, even if they're far apart. This is called **entanglement**.

Because of superposition and entanglement, quantum computers can process a massive amount of data simultaneously and solve certain problems much faster than traditional computers.

Here's a simple analogy: If a traditional computer is like reading a book one page at a time, a quantum computer is like being able to read all the pages at once.

Quantum computing is still a developing field, but it holds great promise for tasks like cryptography, material science, and complex simulations that are beyond the reach of today's classical computers.
(langchain) root@iZ2zea5v77oawjy2qz7c20Z:/data/bank_chatbot#
```


## 并行执行任务代码:

```python
import os
import asyncio
from loguru import logger
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv("env_config/.env.local")

# 创建openai客户端
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_openai_response_unstream(chat_history, task_name):
    """根据历史聊天数据与llm交互,返回结果以非流式输出。
    """
    logger.info(f"Task {task_name} started")
    await asyncio.sleep(3)  # 模拟网络请求延迟
    completion = await client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model=os.getenv('CHAT_MODEL'),
        messages=chat_history,
        # stream=True
    )
    logger.info(f"Task {task_name} completed")
    return completion.choices[0].message.content

async def main():
    chat_history1 = [{"role": "user", "content": "Tell me a joke."}]
    chat_history2 = [{"role": "user", "content": "Explain quantum computing in simple terms."}]

    # 创建两个异步任务
    task1 = asyncio.create_task(get_openai_response_unstream(chat_history1, "Task 1"))
    task2 = asyncio.create_task(get_openai_response_unstream(chat_history2, "Task 2"))

    # 等待任务完成并获取结果
    response1 = await task1
    response2 = await task2

    # 处理结果
    logger.info(f"Response 1: {response1}")
    logger.info(f"Response 2: {response2}")

if __name__ == "__main__":
    asyncio.run(main())
```

终端显示:

```log
(langchain) root@iZ2zea5v77oawjy2qz7c20Z:/data/bank_chatbot# python tests/test_create_mul_tasks_log_test2.py 
2024-06-04 13:51:45.900 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 1 started
2024-06-04 13:51:45.901 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 2 started
2024-06-04 13:51:49.938 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 1 completed
2024-06-04 13:51:55.601 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 2 completed
2024-06-04 13:51:55.601 | INFO     | __main__:main:66 - Response 1: Sure, here's a light-hearted one for you:

Why did the scarecrow win an award?

Because he was outstanding in his field! 🌾😂
2024-06-04 13:51:55.601 | INFO     | __main__:main:67 - Response 2: Sure! Imagine a regular computer as a very fast and precise librarian. It helps you look up and process information using a set series of steps. It holds information in bits, which are like tiny light switches that can be either off (0) or on (1).

Now, think of a quantum computer as a magical librarian with superpowers. Instead of bits, it uses qubits (quantum bits). These qubits have special properties because they follow the rules of quantum mechanics, which is the science of very, very small things like atoms and particles.

Here are the two main superpowers of qubits:

1. **Superposition:** Unlike regular bits that are either 0 or 1, a qubit can be both 0 and 1 at the same time! This is like a magical light switch that’s both off and on simultaneously. This power allows quantum computers to explore many possibilities at once, potentially solving complex problems much faster than regular computers.

2. **Entanglement:** When qubits become entangled, the state of one qubit is directly related to the state of another, no matter how far apart they are. Think of it like having a pair of magic dice: if you roll one die and get a result, the other die will show a matching result instantly, even if it's on the other side of the universe. This allows quantum computers to perform coordinated operations on qubits in ways that classical computers can’t.

These superpowers enable quantum computers to tackle certain tasks much more efficiently than regular computers. They're especially good at solving problems that need exploring lots of possibilities simultaneously, like breaking complex codes, optimizing large systems, and simulating molecules for drug discovery.

However, quantum computing is still in its early stages and is quite delicate. Quantum computers need extremely controlled environments to work correctly, and they’re not yet ready to replace regular computers for most everyday tasks. Researchers are actively working on making them more practical and robust.

So, in simple terms, quantum computing is like having a magical librarian with superpowers, making it possible to solve some incredibly complex problems much faster than a regular librarian can!
(langchain) root@iZ2zea5v77oawjy2qz7c20Z:/data/bank_chatbot# 
```


## 对比的结论:

从终端输出的日志来看，我们可以明显看到两种不同的执行方式所带来的时间差异。<br>

### 依次调用异步函数的日志分析

```log
2024-06-04 13:50:21.636 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 1 started
2024-06-04 13:50:25.706 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 1 completed
2024-06-04 13:50:25.706 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 2 started
2024-06-04 13:50:33.501 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 2 completed
2024-06-04 13:50:33.501 | INFO     | __main__:main:62 - Response 1: Sure, here's a light-hearted joke for you:
...
```

- `Task 1` 开始时间：13:50:21.636
- `Task 1` 完成时间：13:50:25.706
- `Task 2` 开始时间：13:50:25.706
- `Task 2` 完成时间：13:50:33.501

总执行时间约为 11.865 秒。<br>

### 并行执行任务的日志分析

```log
2024-06-04 13:51:45.900 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 1 started
2024-06-04 13:51:45.901 | INFO     | __main__:get_openai_response_unstream:42 - Task Task 2 started
2024-06-04 13:51:49.938 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 1 completed
2024-06-04 13:51:55.601 | INFO     | __main__:get_openai_response_unstream:50 - Task Task 2 completed
2024-06-04 13:51:55.601 | INFO     | __main__:main:66 - Response 1: Sure, here's a light-hearted one for you:
...
```

- `Task 1` 开始时间：13:51:45.900
- `Task 2` 开始时间：13:51:45.901
- `Task 1` 完成时间：13:51:49.938
- `Task 2` 完成时间：13:51:55.601

总执行时间约为 9.701 秒。<br>

### 结论

在依次调用异步函数时，总执行时间几乎是两个任务时间的总和，反映了顺序执行的特性。而在并行执行任务时，尽管 `Task 2` 花费了更长的时间，总执行时间明显减少，反映了并行执行的优势。<br>

这表明，通过使用 `asyncio.create_task` 创建并行任务，可以显著提高 I/O 密集型操作的执行效率。尽管单个异步函数本身已经是异步的，利用 `asyncio.create_task` 仍能在整体上进一步优化任务调度和执行时间。<br>

🔥关键在于 "依次调用异步函数" 在执行第一个任务的时候，第二个任务没有运行。而 "并行执行任务" 在执行第一个任务的时候，第二个任务已经开始运行了，节省了这部分时间。<br>