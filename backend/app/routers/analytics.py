from collections import Counter
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.analytics import DailyAnalytics
from app.models.user import User
from app.schemas.analytics import (
    TopQueriesResponse,
    TopQuery,
    UsageDataPoint,
    UsageResponse,
)

router = APIRouter()


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    days = max(1, min(days, 365))
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(DailyAnalytics)
        .where(
            DailyAnalytics.workspace_id == current_user.workspace_id,
            DailyAnalytics.date >= start_date,
        )
        .order_by(DailyAnalytics.date.asc())
    )
    records = result.scalars().all()

    data = []
    total_queries = 0
    total_tokens = 0

    for r in records:
        data.append(
            UsageDataPoint(
                date=r.date.isoformat(),
                queries=r.total_queries,
                tokens_prompt=r.total_tokens_prompt,
                tokens_completion=r.total_tokens_completion,
                avg_latency_ms=r.average_latency_ms,
            )
        )
        total_queries += r.total_queries
        total_tokens += r.total_tokens_prompt + r.total_tokens_completion

    return UsageResponse(
        data=data,
        total_queries=total_queries,
        total_tokens=total_tokens,
    )


@router.get("/top-queries", response_model=TopQueriesResponse)
async def get_top_queries(
    days: int = 30,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    days = max(1, min(days, 365))
    limit = max(1, min(limit, 100))
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(DailyAnalytics.query_texts)
        .where(
            DailyAnalytics.workspace_id == current_user.workspace_id,
            DailyAnalytics.date >= start_date,
            DailyAnalytics.query_texts.isnot(None),
        )
    )

    all_queries: list[str] = []
    for (query_texts,) in result:
        if query_texts:
            all_queries.extend(query_texts)

    counter = Counter(all_queries)
    top = counter.most_common(limit)

    return TopQueriesResponse(
        queries=[TopQuery(query=q, count=c) for q, c in top]
    )
