import asyncio, os, collections
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    per = collections.defaultdict(lambda: collections.Counter())
    async for d in db.sendgrid_usage.find({}, {"_id": 0}):
        per[d["at"][:10]][d["caller"]] += d.get("recipients", 1)
    for day in sorted(per, reverse=True)[:7]:
        print(f"\n{day}: {sum(per[day].values())} recipients/mails")
        for k, n in per[day].most_common(12):
            print(f"  {n:4}  {k}")
    if not per:
        print("No sends recorded yet.")

asyncio.run(main())
