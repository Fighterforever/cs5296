"""DynamoDB-backed storage for the shortener. In-memory fallback for local dev."""
from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.config import Config


@dataclass
class Record:
    code: str
    url: str
    created: int
    hits: int


class Storage:
    def put(self, code: str, url: str) -> Record: ...
    def get(self, code: str) -> Optional[Record]: ...
    def bump(self, code: str) -> None: ...


class MemoryStore(Storage):
    def __init__(self) -> None:
        self._d: dict[str, Record] = {}
        self._lock = threading.Lock()

    def put(self, code: str, url: str) -> Record:
        rec = Record(code=code, url=url, created=int(time.time()), hits=0)
        with self._lock:
            self._d[code] = rec
        return rec

    def get(self, code: str) -> Optional[Record]:
        with self._lock:
            return self._d.get(code)

    def bump(self, code: str) -> None:
        with self._lock:
            r = self._d.get(code)
            if r:
                r.hits += 1


class DynamoStore(Storage):
    def __init__(self, table: str, region: str) -> None:
        cfg = Config(
            region_name=region,
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=1.0,
            read_timeout=2.0,
            max_pool_connections=64,
        )
        self._table = boto3.resource("dynamodb", config=cfg).Table(table)

    def put(self, code: str, url: str) -> Record:
        now = int(time.time())
        self._table.put_item(
            Item={"code": code, "url": url, "created": now, "hits": 0},
            ConditionExpression="attribute_not_exists(code)",
        )
        return Record(code=code, url=url, created=now, hits=0)

    def get(self, code: str) -> Optional[Record]:
        resp = self._table.get_item(Key={"code": code}, ConsistentRead=False)
        it = resp.get("Item")
        if not it:
            return None
        return Record(code=it["code"], url=it["url"], created=int(it.get("created", 0)), hits=int(it.get("hits", 0)))

    def bump(self, code: str) -> None:
        try:
            self._table.update_item(
                Key={"code": code},
                UpdateExpression="ADD hits :one",
                ExpressionAttributeValues={":one": 1},
                ConditionExpression="attribute_exists(code)",
            )
        except Exception:
            pass


def build_storage() -> Storage:
    table = os.environ.get("DDB_TABLE")
    region = os.environ.get("AWS_REGION", "us-east-1")
    if table:
        return DynamoStore(table=table, region=region)
    return MemoryStore()
