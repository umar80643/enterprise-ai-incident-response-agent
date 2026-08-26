import asyncio


async def main():
    print("Worker ready. Production deployments connect this process to Redis/ARQ job queues.")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
