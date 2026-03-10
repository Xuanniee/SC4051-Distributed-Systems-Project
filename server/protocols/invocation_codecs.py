"""
Files stores the invokation headers for different semantics that wraps every request
"""
from __future__ import annotations

from models.messages import RequestMeta
from protocols.marshaller import BufferReader, BufferWriter

def encode_invocation_header(client_id: str, request_id: int) -> bytes:
    """
    Encode the header with the client id and request id to uniquyely identify all requests
    """
    writer = BufferWriter()
    writer.write_str(client_id)
    writer.write_u32(request_id)

    return writer.to_bytes()

def decode_invocation_header(payload: bytes) -> tuple[RequestMeta, bytes]:
    """
    Payload format:
    [client_id][request_id][actual request body]
    Returns (RequestMeta, remaining_request_body)
    """
    reader = BufferReader(payload)
    client_id = reader.read_str()
    request_id = reader.read_u32()

    remaining_body = payload[len(payload) - reader.remaining():]
    return RequestMeta(client_id=client_id, request_id=request_id), remaining_body