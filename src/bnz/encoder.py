"""Encode an NZB XML file into the BNZ binary format."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass
from io import BytesIO

from bnz.varint import encode_signed, encode_unsigned

MAGIC = b"BNZ\x02"
FLAG_ZLIB = 0x01
FILE_FLAG_CUSTOM_SEG_NUMS = 0x01
NZB_NAMESPACES = (
    "http://www.newzbin.com/DTD/2003/nzb",
    "https://www.newzbin.com/DTD/2003/nzb",
)


@dataclass
class Segment:
    number: int
    bytes_: int
    message_id: str


@dataclass
class NzbFile:
    poster: str
    date: int
    subject: str
    groups: list[str]
    segments: list[Segment]


@dataclass
class NzbDocument:
    meta: dict[str, str]
    files: list[NzbFile]


def _detect_ns(root: ET.Element) -> str:
    tag = root.tag
    if tag.startswith("{"):
        ns = tag[1:].split("}")[0]
        if ns in NZB_NAMESPACES:
            return ns
    for ns in NZB_NAMESPACES:
        if root.tag == f"{{{ns}}}nzb":
            return ns
    return NZB_NAMESPACES[0]


def _has_non_sequential_numbers(segments: list[Segment]) -> bool:
    return any(seg.number != i + 1 for i, seg in enumerate(segments))


def parse_nzb(path: str) -> NzbDocument:
    tree = ET.parse(path)
    root = tree.getroot()
    ns_uri = _detect_ns(root)
    ns = {"n": ns_uri}

    meta: dict[str, str] = {}
    head = root.find("n:head", ns)
    if head is not None:
        for m in head.findall("n:meta", ns):
            key = m.get("type", "")
            value = (m.text or "").strip()
            if key:
                meta[key] = value

    files: list[NzbFile] = []
    for file_el in root.findall("n:file", ns):
        poster = file_el.get("poster", "")
        date = int(file_el.get("date", "0"))
        subject = file_el.get("subject", "")

        groups: list[str] = []
        groups_el = file_el.find("n:groups", ns)
        if groups_el is not None:
            for g in groups_el.findall("n:group", ns):
                if g.text:
                    groups.append(g.text)

        segments: list[Segment] = []
        segs_el = file_el.find("n:segments", ns)
        if segs_el is not None:
            for s in segs_el.findall("n:segment", ns):
                seg_bytes = int(s.get("bytes", "0"))
                seg_num = int(s.get("number", "0"))
                seg_id = (s.text or "").strip()
                segments.append(Segment(number=seg_num, bytes_=seg_bytes, message_id=seg_id))

        files.append(NzbFile(
            poster=poster,
            date=date,
            subject=subject,
            groups=groups,
            segments=segments,
        ))

    return NzbDocument(meta=meta, files=files)


class StringTable:
    def __init__(self) -> None:
        self._strings: list[str] = []
        self._index: dict[str, int] = {}

    def add(self, s: str) -> int:
        if s in self._index:
            return self._index[s]
        idx = len(self._strings)
        self._strings.append(s)
        self._index[s] = idx
        return idx

    @property
    def entries(self) -> list[str]:
        return self._strings


def _build_string_table(doc: NzbDocument) -> StringTable:
    table = StringTable()
    for key, value in doc.meta.items():
        table.add(key)
        table.add(value)
    for f in doc.files:
        table.add(f.poster)
        table.add(f.subject)
        for g in f.groups:
            table.add(g)
        for seg in f.segments:
            table.add(seg.message_id)
    return table


def _write_varint(buf: BytesIO, value: int) -> None:
    buf.write(encode_unsigned(value))


def _write_signed_varint(buf: BytesIO, value: int) -> None:
    buf.write(encode_signed(value))


def encode(doc: NzbDocument) -> bytes:
    table = _build_string_table(doc)

    payload = BytesIO()

    _write_varint(payload, len(doc.files))

    _write_varint(payload, len(table.entries))
    for s in table.entries:
        encoded = s.encode("utf-8")
        _write_varint(payload, len(encoded))
        payload.write(encoded)

    _write_varint(payload, len(doc.meta))
    for key, value in doc.meta.items():
        _write_varint(payload, table.add(key))
        _write_varint(payload, table.add(value))

    for f in doc.files:
        _write_varint(payload, table.add(f.poster))
        _write_varint(payload, f.date)
        _write_varint(payload, table.add(f.subject))

        custom_nums = _has_non_sequential_numbers(f.segments)
        file_flags = FILE_FLAG_CUSTOM_SEG_NUMS if custom_nums else 0
        _write_varint(payload, file_flags)

        _write_varint(payload, len(f.groups))
        for g in f.groups:
            _write_varint(payload, table.add(g))
        _write_varint(payload, len(f.segments))

        if custom_nums:
            prev_num = 0
            for seg in f.segments:
                _write_signed_varint(payload, seg.number - prev_num)
                prev_num = seg.number

        prev_bytes = 0
        for seg in f.segments:
            delta = seg.bytes_ - prev_bytes
            _write_signed_varint(payload, delta)
            prev_bytes = seg.bytes_
            _write_varint(payload, table.add(seg.message_id))

    raw = payload.getvalue()
    compressed = zlib.compress(raw, 9)

    use_zlib = len(compressed) < len(raw)
    out = BytesIO()
    out.write(MAGIC)
    out.write(bytes([FLAG_ZLIB if use_zlib else 0]))
    if use_zlib:
        _write_varint(out, len(raw))
        out.write(compressed)
    else:
        out.write(raw)

    return out.getvalue()


def encode_file(nzb_path: str, bnz_path: str) -> tuple[int, int]:
    import os

    doc = parse_nzb(nzb_path)
    data = encode(doc)
    with open(bnz_path, "wb") as f:
        f.write(data)
    return os.path.getsize(nzb_path), len(data)
