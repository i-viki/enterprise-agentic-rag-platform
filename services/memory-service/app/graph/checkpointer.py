from langgraph.checkpoint.memory import MemorySaver
import structlog

logger = structlog.get_logger(__name__)

def get_checkpointer():
    """Returns persistent checkpointer for multi-turn threads."""
    # MemorySaver operates with zero disk friction for local runtime;
    # Can be swapped to AsyncPostgresSaver for enterprise production clustering
    return MemorySaver()

