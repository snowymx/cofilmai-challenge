# main.py

import os
from src.apis import apis
from prisma import Prisma
from fastapi import FastAPI, BackgroundTasks, HTTPException
from TikTokApi import TikTokApi
from typing import List

app = FastAPI()
app.include_router(apis, prefix="/apis")
prisma = Prisma(
    datasource={
        'url': os.environ.get('DATA\BASE_URL'),
    }
)

def fetch_and_store_trends(country):
    try:
        tiktok_api = TikTokApi.get_instance()
        trends = tiktok_api.by_trending(count=10, custom_verifyFp="")
        for trend in trends:
            hashtags = [tag["title"] for tag in trend.get("challenges", [])]
            music = {
                "title": trend["music"]["title"],
                "author": trend["music"]["authorName"],
            }
            prisma.trend.create(
                data={
                    "country": country,
                    "title": trend["desc"],
                    "url": trend["link"],
                    "hashtags": hashtags,
                    "music": music,
                }
            )
        return f"Trends for {country} fetched and stored successfully."
    except Exception as e:
        return f"Error fetching and storing trends for {country}: {str(e)}"

# Event handlers
@app.on_event("startup")
async def startup():
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()

# Default route
@app.get("/")
def read_root():
    return {"version": "1.0.0"}

# Route to initiate background task for fetching trends by country
@app.post("/fetch-trends/{country}")
async def fetch_trends_by_country(
    country: str,
    background_tasks: BackgroundTasks,
    interval: int = 3600,
):
    # Add a background task to fetch and store trends
    background_tasks.add_task(fetch_and_store_trends, country)

    # Schedule periodic background task for fetching and storing trends
    periodic_task = fetch_and_store_trends.s(country)
    periodic_task.apply_async(countdown=interval, repeat=True)

    return {
        "message": f"Fetching and storing TikTok trends for {country}. Task scheduled to run every {interval} seconds."
    }

# Endpoint to get all trends
@app.get("/trends", response_model=List[dict])
def get_all_trends():
    trends = prisma.trend.find_many()
    return {"trends": trends}

# Endpoint to get trends by country
@app.get("/trends/{country}", response_model=List[dict])
def get_trends_by_country(country: str):
    trends = prisma.trend.find_many(where={"country": country})
    return {"trends": trends}

# Endpoint to update a trend by ID
@app.put("/trends/{trend_id}")
def update_trend(trend_id: int, updated_trend: dict):
    existing_trend = prisma.trend.find_unique(where={"id": trend_id})
    if existing_trend:
        prisma.trend.update(where={"id": trend_id}, data=updated_trend)
        return {"message": f"Trend {trend_id} updated successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Trend {trend_id} not found")

# Endpoint to delete a trend by ID
@app.delete("/trends/{trend_id}")
def delete_trend(trend_id: int):
    existing_trend = prisma.trend.find_unique(where={"id": trend_id})
    if existing_trend:
        prisma.trend.delete(where={"id": trend_id})
        return {"message": f"Trend {trend_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Trend {trend_id} not found")


# Endpoint to list trending posts by topic or set of hashtags
@app.get("/trending-posts")
def list_trending_posts_by_topic_or_hashtags(
    topic: str = None,
    hashtags: List[str] = None,
    limit: int = 10,
):
    if not topic and not hashtags:
        raise HTTPException(status_code=400, detail="Either 'topic' or 'hashtags' must be provided.")

    # Fetch trends based on topic or hashtags
    where_clause = {}
    if topic:
        where_clause["title"] = {"contains": topic}
    if hashtags:
        where_clause["hashtags"] = {"has": hashtags}

    trends = prisma.trend.find_many(
        where=where_clause,
        take=limit,
    )
    return {"trends": trends}

# Endpoint to list trending hashtags by country
@app.get("/trending-hashtags/{country}")
def list_trending_hashtags(
    country: str,
    limit: int = 10,
):
    trends = prisma.trend.find_many(
        where={"country": country},
        order=[{"views": "desc"}],
        take=limit,
    )
    hashtags = [tag for trend in trends for tag in trend.get("hashtags", [])]
    return {"hashtags": hashtags}

