import asyncio
from config import NOTIFICATION_BIN_INTERVAL
from utils.notifications import send_user_notifications
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def start_notification_scheduler(scheduler):
    scheduler.add_job(send_user_notifications, trigger='interval', minutes=NOTIFICATION_BIN_INTERVAL)
    scheduler.start()
    print("Notification scheduler started")

async def shutdown_scheduler(scheduler):
    scheduler.shutdown()
    print("Notification scheduler stopped")

async def main():
    scheduler = AsyncIOScheduler()
    try:
        await start_notification_scheduler(scheduler)
        await asyncio.Future()  

    except KeyboardInterrupt:
        await shutdown_scheduler(scheduler)

if __name__ == "__main__":
    asyncio.run(main())

