from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class NodeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class Node(BaseModel):
    node_id: str
    cpu_cores: int
    status: NodeStatus = NodeStatus.ACTIVE
    pods: List[str] = []


class NodeCreate(BaseModel):
    cpu_cores: int
