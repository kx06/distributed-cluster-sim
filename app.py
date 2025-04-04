import os
from enum import Enum
from typing import Optional  # <--- ADD THIS IMPORT

import requests
import streamlit as st
from pydantic import BaseModel, Field, ValidationError, field_validator

# --- Configuration ---
# Use environment variable or default for API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# --- Pydantic Models (matching backend schemas.py) ---
# It's good practice to define expected structures, even in the frontend
class NodeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class Node(BaseModel):
    node_id: str
    cpu_cores: int
    status: NodeStatus = NodeStatus.ACTIVE
    pods: list[str] = []


class NodeCreate(BaseModel):
    cpu_cores: int = Field(..., gt=0)  # Ensure positive integer


# --- API Interaction Functions ---


def get_api_nodes() -> dict[str, Node]:
    """Fetches all nodes from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/nodes/")
        response.raise_for_status()  # Raise exception for bad status codes (4xx or 5xx)
        nodes_data = response.json()
        # Validate fetched data against our Pydantic model
        validated_nodes = {}
        for node_id, node_data in nodes_data.items():
            try:
                validated_nodes[node_id] = Node(**node_data)
            except ValidationError as e:
                st.warning(f"Invalid data received for node {node_id}: {e}. Skipping.")
        return validated_nodes
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}")
        return {}
    except ValueError:  # Includes JSONDecodeError
        st.error("Error: Invalid JSON received from API.")
        return {}
    except ValidationError as e:
        st.error(f"API response structure mismatch: {e}")
        return {}


def add_api_node(cpu_cores: int) -> Optional[Node]:
    """Adds a new node via the API."""
    try:
        node_create_data = NodeCreate(cpu_cores=cpu_cores)  # Validate input
        response = requests.post(
            f"{API_BASE_URL}/nodes/",
            json=node_create_data.model_dump(),  # Use model_dump for Pydantic v2+
        )
        response.raise_for_status()
        new_node_data = response.json()
        return Node(**new_node_data)  # Validate response
    except ValidationError as e:
        st.error(f"Invalid input for CPU cores: {e}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error adding node via API: {e}")
        # Check for specific messages if possible
        try:
            detail = response.json().get("detail")
            if detail:
                st.error(f"API Error Detail: {detail}")
        except Exception:
            pass  # Ignore if parsing detail fails
        return None
    except ValueError:  # Includes JSONDecodeError
        st.error("Error: Invalid JSON received after adding node.")
        return None


def remove_api_node(node_id: str) -> bool:
    """Removes a node via the API."""
    try:
        response = requests.delete(f"{API_BASE_URL}/nodes/{node_id}")
        response.raise_for_status()
        st.toast(f"Node {node_id} removed successfully!", icon="✅")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error removing node {node_id}: {e}")
        # Check for specific messages (like 404 Not Found)
        try:
            detail = response.json().get("detail")
            if response.status_code == 404:
                st.error(f"Node {node_id} not found on the server.")
            elif detail:
                st.error(f"API Error Detail: {detail}")
        except Exception:
            pass  # Ignore if parsing detail fails
        return False


# --- Streamlit UI ---

st.set_page_config(page_title="Cluster Manager", layout="wide")

st.title(" Distributed System Cluster Simulator")
st.caption(f"Interacting with API at: {API_BASE_URL}")

# --- State Management ---
# Use session state to keep track of nodes between reruns
if "nodes" not in st.session_state:
    st.session_state.nodes = {}


def refresh_nodes():
    """Clears local state and fetches fresh data from API."""
    st.session_state.nodes = get_api_nodes()
    st.rerun()  # Rerun the script to update the UI


# --- Add Node Section ---
st.header("Add New Node", divider="rainbow")
with st.form("add_node_form"):
    cpu_input = st.number_input(
        "CPU Cores for New Node:", min_value=1, step=1, value=2  # Default value
    )
    submitted = st.form_submit_button("Add Node")
    if submitted:
        with st.spinner("Adding node..."):
            new_node = add_api_node(int(cpu_input))
            if new_node:
                st.success(f"Node {new_node.node_id} added successfully!")
                # Immediately refresh the list after adding
                refresh_nodes()
            # Errors are handled within add_api_node using st.error

# --- List Nodes Section ---
st.header("Cluster Nodes", divider="rainbow")

col_refresh, col_info = st.columns([1, 5])

with col_refresh:
    if st.button("Refresh List", use_container_width=True):
        with st.spinner("Fetching nodes..."):
            refresh_nodes()

# Fetch nodes initially if the state is empty
if not st.session_state.nodes:
    with st.spinner("Fetching initial node list..."):
        st.session_state.nodes = get_api_nodes()
        # No rerun needed here as it's part of the initial script run

nodes_list = list(st.session_state.nodes.values())

with col_info:
    st.metric("Total Nodes", len(nodes_list))

if not nodes_list:
    st.info("No nodes found in the cluster. Add one above!")
else:
    # Define columns for the node display
    cols = st.columns([2, 1, 1, 2, 1])  # Adjust widths as needed
    headers = ["Node ID", "CPU Cores", "Status", "Pods", "Actions"]
    for header, col in zip(headers, cols):
        col.subheader(header)

    st.divider()  # Separator between header and nodes

    for node in nodes_list:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])

        with col1:
            st.code(node.node_id, language=None)
        with col2:
            st.metric("", node.cpu_cores)  # Use metric for nice number display
        with col3:
            # Add color/icon based on status if desired later
            st.caption(node.status.value)
        with col4:
            # Display pods (will be empty in Week 1)
            st.caption(str(node.pods) if node.pods else "[]")
        with col5:
            # Use node_id in the key to make each button unique
            if st.button(
                "Remove",
                key=f"remove_{node.node_id}",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner(f"Removing {node.node_id}..."):
                    success = remove_api_node(node.node_id)
                    if success:
                        # Refresh list after successful removal
                        refresh_nodes()  # This triggers a rerun
