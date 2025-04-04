import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api_server import schemas
from api_server.node_manager import NodeManager

Node = schemas.Node
NodeCreate = schemas.NodeCreate


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Distributed Cluster Simulation API")
node_manager = NodeManager()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/nodes/", response_model=Node)
def add_node(node_create: NodeCreate):
    """Add a new node to the cluster"""
    return node_manager.add_node(node_create.cpu_cores)


@app.get("/nodes/", response_model=dict)
def list_nodes():
    """List all nodes in the cluster"""
    return node_manager.get_all_nodes()


@app.get("/nodes/{node_id}", response_model=Node)
def get_node(node_id: str):
    """Get details of a specific node"""
    node = node_manager.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@app.delete("/nodes/{node_id}")
def remove_node(node_id: str):
    """Remove a node from the cluster"""
    if not node_manager.remove_node(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node removed successfully"}
