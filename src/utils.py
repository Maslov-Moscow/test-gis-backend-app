import asyncio
import os
from concurrent.futures import ProcessPoolExecutor

process_executor = ProcessPoolExecutor(max_workers=os.cpu_count())

async def submit_to_process_executor(func, *args, **kwargs):
    """
    Асинхронно вызывает sync-функцию в process pool.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_executor, func, *args)