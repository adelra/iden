import uuid
import base58

def shortuuid() -> str:
    """
    Generates a short, URL-safe UUID.
    """
    return base58.b58encode(uuid.uuid4().bytes).decode("utf-8")
