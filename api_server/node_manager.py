import logging
from typing import Dict, Optional
from uuid import uuid4

from api_server import schemas

Node = schemas.Node
NodeStatus = schemas.NodeStatus


class NodeManager:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.logger = logging.getLogger(__name__)

    def add_node(self, cpu_cores: int) -> Node:
        """Add a new node to the cluster"""
        node_id = str(uuid4())
        new_node = Node(node_id=node_id, cpu_cores=cpu_cores, status=NodeStatus.ACTIVE)
        self.nodes[node_id] = new_node
        self.logger.info(f"Added new node {node_id} with {cpu_cores} CPU cores")
        return new_node

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by its ID"""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> Dict[str, Node]:
        """Get all nodes in the cluster"""
        return self.nodes

    def update_node_status(self, node_id: str, status: NodeStatus) -> bool:
        """Update a node's status"""
        if node_id not in self.nodes:
            self.logger.warning(f"Node {node_id} not found for status update")
            return False

        self.nodes[node_id].status = status
        self.logger.info(f"Updated node {node_id} status to {status}")
        return True

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the cluster"""
        if node_id not in self.nodes:
            self.logger.warning(f"Node {node_id} not found for removal")
            return False

        del self.nodes[node_id]
        self.logger.info(f"Removed node {node_id} from cluster")
        return True
