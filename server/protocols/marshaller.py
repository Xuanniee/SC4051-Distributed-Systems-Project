from __future__ import annotations
import struct

class BufferWriter:
    """
    Serializes Python values into bytes using network byte order (big-endian).
    Suitable for UDP request/reply payload construction.
    """
    def __init__(self) -> None:
        self._buffer = bytearray()

    def write_u8(self, value: int) -> None:
        if not 0 <= value <= 0xFF:
            raise ValueError(f"u8 out of range: {value}")
        self._buffer += struct.pack("!B", value)

    def write_u32(self, value: int) -> None:
        if not 0 <= value <= 0xFFFFFFFF:
            raise ValueError(f"u32 out of range: {value}")
        self._buffer += struct.pack("!I", value)

    def write_f64(self, value: float) -> None:
        self._buffer += struct.pack("!d", float(value))

    def write_bytes(self, value: bytes) -> None:
        self.write_u32(len(value))
        self._buffer += value

    def write_str(self, value: str) -> None:
        encoded = value.encode("utf-8")
        self.write_u32(len(encoded))
        self._buffer += encoded

    def to_bytes(self) -> bytes:
        return bytes(self._buffer)

class BufferReader:
    """
    Deserializes bytes into Python values using network byte order (big-endian).
    """
    def __init__(self, data: bytes) -> None:
        self._buffer = data
        self._offset = 0

    def _read_exact(self, size: int) -> bytes:
        end = self._offset + size
        if end > len(self._buffer):
            raise ValueError(
                f"Not enough bytes to read {size} byte(s). "
                f"Offset={self._offset}, buffer_length={len(self._buffer)}"
            )
        chunk = self._buffer[self._offset:end]
        self._offset = end
        return chunk

    def read_u8(self) -> int:
        return struct.unpack("!B", self._read_exact(1))[0]

    def read_u32(self) -> int:
        return struct.unpack("!I", self._read_exact(4))[0]

    def read_f64(self) -> float:
        return struct.unpack("!d", self._read_exact(8))[0]

    def read_bytes(self) -> bytes:
        length = self.read_u32()
        return self._read_exact(length)

    def read_str(self) -> str:
        length = self.read_u32()
        raw = self._read_exact(length)
        return raw.decode("utf-8")

    def remaining(self) -> int:
        return len(self._buffer) - self._offset

    def has_remaining(self) -> bool:
        return self.remaining() > 0