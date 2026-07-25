"""Decode a BNZ binary file back into NZB XML."""

from __future__ import annotations

import zlib
from io import BytesIO

from bnz.encoder import (
    FILE_FLAG_CUSTOM_SEG_NUMS,
    FLAG_ZLIB,
    MAGIC,
    NZB_NAMESPACES,
    NzbDocument,
    NzbFile,
    Segment,
)
from bnz.varint import decode_signed, decode_unsigned

_NZB_NS = NZB_NAMESPACES[0]


class _Reader:
    def __init__(self, data: bytes) -> None:
        self._buf = BytesIO(data)

    def read_varint(self) -> int:
        val, _ = decode_unsigned(self._buf)
        return val

    def read_signed_varint(self) -> int:
        val, _ = decode_signed(self._buf)
        return val

    def read_bytes(self, n: int) -> bytes:
        data = self._buf.read(n)
        if len(data) != n:
            raise ValueError(f"Expected {n} bytes, got {len(data)}")
        return data

    @property
    def remaining(self) -> int:
        pos = self._buf.tell()
        end = len(self._buf.getvalue())
        return end - pos


def decode(data: bytes) -> NzbDocument:
    if len(data) < 5:
        raise ValueError("Not a valid BNZ file: too short")

    magic = data[:4]
    if magic != MAGIC:
        if magic == b"BNZ\x01":
            raise ValueError(
                "BNZ v1 format detected. This file was created with an older version "
                "that silently dropped segment numbers. Re-encode from the original NZB."
            )
        raise ValueError(f"Not a valid BNZ file: bad magic {magic!r}")

    flags = data[4]
    use_zlib = (flags & FLAG_ZLIB) != 0

    reader = _Reader(data[5:])

    if use_zlib:
        uncompressed_size = reader.read_varint()
        compressed = reader.read_bytes(reader.remaining)
        payload = zlib.decompress(compressed, bufsize=uncompressed_size)
        reader = _Reader(payload)
    else:
        payload = reader.read_bytes(reader.remaining)
        reader = _Reader(payload)

    num_files = reader.read_varint()

    num_strings = reader.read_varint()
    strings: list[str] = []
    for _ in range(num_strings):
        slen = reader.read_varint()
        sdata = reader.read_bytes(slen)
        strings.append(sdata.decode("utf-8"))

    num_meta = reader.read_varint()
    meta: dict[str, str] = {}
    for _ in range(num_meta):
        key_idx = reader.read_varint()
        val_idx = reader.read_varint()
        meta[strings[key_idx]] = strings[val_idx]

    files: list[NzbFile] = []
    for _ in range(num_files):
        poster_idx = reader.read_varint()
        date = reader.read_varint()
        subject_idx = reader.read_varint()

        file_flags = reader.read_varint()
        has_custom_seg_nums = (file_flags & FILE_FLAG_CUSTOM_SEG_NUMS) != 0

        num_groups = reader.read_varint()
        groups: list[str] = []
        for _ in range(num_groups):
            g_idx = reader.read_varint()
            groups.append(strings[g_idx])

        num_segments = reader.read_varint()

        seg_numbers: list[int] = []
        if has_custom_seg_nums:
            prev_num = 0
            for _ in range(num_segments):
                delta = reader.read_signed_varint()
                prev_num += delta
                seg_numbers.append(prev_num)

        segments: list[Segment] = []
        prev_bytes = 0
        for i in range(num_segments):
            delta = reader.read_signed_varint()
            prev_bytes += delta
            msg_idx = reader.read_varint()
            seg_num = seg_numbers[i] if has_custom_seg_nums else i + 1
            segments.append(Segment(
                number=seg_num,
                bytes_=prev_bytes,
                message_id=strings[msg_idx],
            ))

        files.append(NzbFile(
            poster=strings[poster_idx],
            date=date,
            subject=strings[subject_idx],
            groups=groups,
            segments=segments,
        ))

    return NzbDocument(meta=meta, files=files)


def _escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def to_xml(doc: NzbDocument) -> str:
    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<nzb xmlns="{_NZB_NS}">',
    ]

    if doc.meta:
        lines.append("<head>")
        for key, value in doc.meta.items():
            lines.append(f' <meta type="{_escape_xml(key)}">{_escape_xml(value)}</meta>')
        lines.append("</head>")

    for f in doc.files:
        lines.append(
            f'<file poster="{_escape_xml(f.poster)}" date="{f.date}"'
            f' subject="{_escape_xml(f.subject)}">'
        )
        lines.append(" <groups>")
        for g in f.groups:
            lines.append(f"  <group>{_escape_xml(g)}</group>")
        lines.append(" </groups>")
        lines.append(" <segments>")
        for seg in f.segments:
            lines.append(
                f'  <segment bytes="{seg.bytes_}" number="{seg.number}">'
                f"{_escape_xml(seg.message_id)}</segment>"
            )
        lines.append(" </segments>")
        lines.append("</file>")

    lines.append("</nzb>")
    return "\n".join(lines) + "\n"


def decode_file(bnz_path: str, nzb_path: str) -> tuple[int, int]:
    with open(bnz_path, "rb") as f:
        data = f.read()
    doc = decode(data)
    xml = to_xml(doc)
    xml_bytes = xml.encode("utf-8")
    with open(nzb_path, "wb") as f:
        f.write(xml_bytes)
    return len(data), len(xml_bytes)
