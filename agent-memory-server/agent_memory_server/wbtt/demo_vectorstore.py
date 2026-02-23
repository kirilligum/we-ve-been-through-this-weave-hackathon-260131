from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis

from agent_memory_server.filters import (
    CreatedAt,
    DiscreteMemoryExtracted,
    Entities,
    EventDate,
    Id,
    LastAccessed,
    MemoryHash,
    MemoryType,
    Namespace,
    SessionId,
    Topics,
    UserId,
)
from agent_memory_server.models import MemoryRecord, MemoryRecordResult, MemoryRecordResults
from agent_memory_server.utils.redis import get_redis_conn
from agent_memory_server.vectorstore_adapter import VectorStoreAdapter


_KEY_PREFIX = "wbtt_demo:memory"
_ID_SET_KEY = "wbtt_demo:memory:ids"


def create_demo_vectorstore(_embeddings) -> "DemoRedisVectorStoreAdapter":
    """Factory for demo vectorstore that does not require RediSearch."""
    return DemoRedisVectorStoreAdapter()


class DemoRedisVectorStoreAdapter(VectorStoreAdapter):
    """Minimal Redis-backed adapter for demos (no RediSearch required)."""

    def __init__(self) -> None:
        super().__init__(vectorstore=None, embeddings=None)

    async def add_memories(self, memories: list[MemoryRecord]) -> list[str]:
        if not memories:
            return []
        redis = await _redis()
        ids: list[str] = []
        for mem in memories:
            ids.append(mem.id)
            key = _memory_key(mem.id)
            await redis.hset(
                key,
                mapping=_memory_to_hash(mem),
            )
            await redis.sadd(_ID_SET_KEY, mem.id)
        return ids

    async def search_memories(
        self,
        query: str,
        session_id: SessionId | None = None,
        user_id: UserId | None = None,
        namespace: Namespace | None = None,
        created_at: CreatedAt | None = None,
        last_accessed: LastAccessed | None = None,
        topics: Topics | None = None,
        entities: Entities | None = None,
        memory_type: MemoryType | None = None,
        event_date: EventDate | None = None,
        memory_hash: MemoryHash | None = None,
        id: Id | None = None,
        discrete_memory_extracted: DiscreteMemoryExtracted | None = None,
        distance_threshold: float | None = None,
        server_side_recency: bool | None = None,
        recency_params: dict | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> MemoryRecordResults:
        # Ignore vector distance and recency in demo mode.
        return await self._list_or_search(
            query=query,
            session_id=session_id,
            user_id=user_id,
            namespace=namespace,
            created_at=created_at,
            last_accessed=last_accessed,
            topics=topics,
            entities=entities,
            memory_type=memory_type,
            event_date=event_date,
            memory_hash=memory_hash,
            id=id,
            discrete_memory_extracted=discrete_memory_extracted,
            limit=limit,
            offset=offset,
        )

    async def list_memories(
        self,
        session_id: SessionId | None = None,
        user_id: UserId | None = None,
        namespace: Namespace | None = None,
        created_at: CreatedAt | None = None,
        last_accessed: LastAccessed | None = None,
        topics: Topics | None = None,
        entities: Entities | None = None,
        memory_type: MemoryType | None = None,
        event_date: EventDate | None = None,
        memory_hash: MemoryHash | None = None,
        id: Id | None = None,
        discrete_memory_extracted: DiscreteMemoryExtracted | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> MemoryRecordResults:
        return await self._list_or_search(
            query="",
            session_id=session_id,
            user_id=user_id,
            namespace=namespace,
            created_at=created_at,
            last_accessed=last_accessed,
            topics=topics,
            entities=entities,
            memory_type=memory_type,
            event_date=event_date,
            memory_hash=memory_hash,
            id=id,
            discrete_memory_extracted=discrete_memory_extracted,
            limit=limit,
            offset=offset,
        )

    async def delete_memories(self, memory_ids: list[str]) -> int:
        if not memory_ids:
            return 0
        redis = await _redis()
        deleted = 0
        for mem_id in memory_ids:
            key = _memory_key(mem_id)
            if await redis.delete(key):
                deleted += 1
            await redis.srem(_ID_SET_KEY, mem_id)
        return deleted

    async def update_memories(self, memories: list[MemoryRecord]) -> int:
        if not memories:
            return 0
        redis = await _redis()
        updated = 0
        for mem in memories:
            key = _memory_key(mem.id)
            if await redis.exists(key):
                await redis.hset(key, mapping=_memory_to_hash(mem))
                updated += 1
            else:
                await redis.hset(key, mapping=_memory_to_hash(mem))
            await redis.sadd(_ID_SET_KEY, mem.id)
        return updated

    async def count_memories(
        self,
        namespace: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> int:
        # Cheap count that ignores filters.
        redis = await _redis()
        return int(await redis.scard(_ID_SET_KEY))

    async def _list_or_search(
        self,
        *,
        query: str,
        session_id: SessionId | None,
        user_id: UserId | None,
        namespace: Namespace | None,
        created_at: CreatedAt | None,
        last_accessed: LastAccessed | None,
        topics: Topics | None,
        entities: Entities | None,
        memory_type: MemoryType | None,
        event_date: EventDate | None,
        memory_hash: MemoryHash | None,
        id: Id | None,
        discrete_memory_extracted: DiscreteMemoryExtracted | None,
        limit: int,
        offset: int,
    ) -> MemoryRecordResults:
        redis = await _redis()
        ids = list(await redis.smembers(_ID_SET_KEY))
        query_lower = (query or "").lower()
        results: list[MemoryRecordResult] = []

        for raw_id in ids:
            mem_id = raw_id.decode() if isinstance(raw_id, bytes) else raw_id
            key = _memory_key(mem_id)
            data = await redis.hgetall(key)
            if not data:
                continue
            record = _hash_to_memory(mem_id, data)

            if not _matches_filters(
                record,
                session_id=session_id,
                user_id=user_id,
                namespace=namespace,
                memory_type=memory_type,
            ):
                continue

            if query_lower and query_lower not in record.text.lower():
                continue

            results.append(
                MemoryRecordResult(
                    **record.model_dump(),
                    dist=1.0,
                )
            )

        total = len(results)
        sliced = results[offset : offset + limit]
        next_offset = offset + limit if total > offset + limit else None
        return MemoryRecordResults(memories=sliced, total=total, next_offset=next_offset)


async def _redis() -> Redis:
    return await get_redis_conn()


def _memory_key(mem_id: str) -> str:
    return f"{_KEY_PREFIX}:{mem_id}"


def _memory_to_hash(mem: MemoryRecord) -> dict[str, Any]:
    memory_type = mem.memory_type
    try:
        memory_type_value = memory_type.value  # type: ignore[union-attr]
    except AttributeError:
        memory_type_value = str(memory_type)
    return {
        "id": mem.id,
        "text": mem.text,
        "session_id": mem.session_id or "",
        "user_id": mem.user_id or "",
        "namespace": mem.namespace or "",
        "memory_type": memory_type_value,
        "created_at": _dt_to_str(mem.created_at),
        "updated_at": _dt_to_str(mem.updated_at),
        "last_accessed": _dt_to_str(mem.last_accessed),
    }


def _hash_to_memory(mem_id: str, data: dict[bytes, bytes]) -> MemoryRecord:
    decoded = {k.decode(): v.decode() for k, v in data.items()}
    raw_type = decoded.get("memory_type") or "semantic"
    if raw_type.startswith("MemoryTypeEnum."):
        raw_type = raw_type.split(".", 1)[-1].lower()
    return MemoryRecord(
        id=mem_id,
        text=decoded.get("text", ""),
        session_id=decoded.get("session_id") or None,
        user_id=decoded.get("user_id") or None,
        namespace=decoded.get("namespace") or None,
        memory_type=raw_type,
        created_at=_str_to_dt(decoded.get("created_at")),
        updated_at=_str_to_dt(decoded.get("updated_at")),
        last_accessed=_str_to_dt(decoded.get("last_accessed")),
    )


def _dt_to_str(value: datetime | None) -> str:
    if not value:
        return ""
    return value.astimezone(timezone.utc).isoformat()


def _str_to_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.now(timezone.utc)


def _matches_filters(
    record: MemoryRecord,
    *,
    session_id: SessionId | None,
    user_id: UserId | None,
    namespace: Namespace | None,
    memory_type: MemoryType | None,
) -> bool:
    if session_id and session_id.eq and record.session_id != session_id.eq:
        return False
    if user_id and user_id.eq and record.user_id != user_id.eq:
        return False
    if namespace and namespace.eq and record.namespace != namespace.eq:
        return False
    if memory_type and memory_type.eq and str(record.memory_type) != memory_type.eq:
        return False
    return True
