import asyncio
import os 

from job_worker import start_bot



async def main():
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass