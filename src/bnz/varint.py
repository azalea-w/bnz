"""Unsigned and signed (zigzag) variable-length integer encoding."""

from __future__ import annotations

from io import BytesIO


def encode_unsigned(value: int) -> bytes:
    if value < 0:
        raise ValueError(f"Cannot encode negative value as unsigned varint: {value}")
    parts: list[int] = []
    while value > 0x7F:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    parts.append(value & 0x7F)
    return bytes(parts)


def decode_unsigned(data: bytes | BytesIO, *, offset: int = 0) -> tuple[int, int]:
    stream = data if isinstance(data, BytesIO) else BytesIO(data)
    if not isinstance(data, BytesIO):
        stream.seek(offset)
    result = 0
    shift = 0
    while True:
        byte = stream.read(1)
        if not byte:
            raise ValueError("Truncated varint")
        b = byte[0]
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result, stream.tell() if isinstance(data, BytesIO) else offset + (shift // 7 + 1)


def zigzag_encode(value: int) -> int:
    return (value << 1) ^ (value >> 63)


def zigzag_decode(value: int) -> int:
    return (value >> 1) ^ -(value & 1)


def encode_signed(value: int) -> bytes:
    return encode_unsigned(zigzag_encode(value))


def decode_signed(data: bytes | BytesIO, *, offset: int = 0) -> tuple[int, int]:
    raw, new_offset = decode_unsigned(data, offset=offset)
    return zigzag_decode(raw), new_offset
