"""CLI for converting between NZB and BNZ formats."""

from __future__ import annotations

import gzip
import os
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from bnz.decoder import decode_file
from bnz.encoder import encode_file

console = Console()


def _ratio(part: int, whole: int) -> str:
    if whole == 0:
        return "N/A"
    return f"{part * 100 / whole:.1f}%"


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _resolve_output(path: str, output_dir: str | None, suffix: str) -> str:
    name = Path(path).stem + suffix
    if output_dir:
        return os.path.join(output_dir, name)
    return os.path.join(os.path.dirname(path) or ".", name)


def cmd_compress(
    paths: list[str],
    *,
    output_dir: str | None = None,
    outer_gzip: bool = False,
) -> None:
    suffix = ".bnz.gz" if outer_gzip else ".bnz"
    total_orig = 0
    total_out = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for path in paths:
            task = progress.add_task(f"Compressing {os.path.basename(path)}...", total=None)
            bnz_path = _resolve_output(path, output_dir, suffix)

            t0 = time.perf_counter()
            orig_size, bnz_size = encode_file(path, bnz_path)
            elapsed = time.perf_counter() - t0

            final_size = bnz_size
            if outer_gzip:
                with open(bnz_path, "rb") as f:
                    raw_bnz = f.read()
                gzipped = gzip.compress(raw_bnz, 9)
                with open(bnz_path, "wb") as f:
                    f.write(gzipped)
                final_size = len(gzipped)

            total_orig += orig_size
            total_out += final_size
            progress.update(
                task,
                description=(
                    f"{os.path.basename(path)}  "
                    f"{_human_size(orig_size)} -> {_human_size(final_size)}  "
                    f"({_ratio(final_size, orig_size)})  [{elapsed:.2f}s]"
                ),
            )

    if len(paths) > 1:
        console.print(
            f"\n[bold]{len(paths)} files[/]  "
            f"{_human_size(total_orig)} -> {_human_size(total_out)}  "
            f"({_ratio(total_out, total_orig)})"
        )


def cmd_decompress(paths: list[str], *, output_dir: str | None = None) -> None:
    for path in paths:
        is_gzipped = path.endswith(".gz")
        stem = Path(path).stem
        if is_gzipped:
            stem = Path(stem).stem
        nzb_path = _resolve_output(path, output_dir, ".nzb")

        with open(path, "rb") as f:
            raw = f.read()

        if is_gzipped:
            raw = gzip.decompress(raw)

        tmp_bnz = path + ".__tmp_decode"
        with open(tmp_bnz, "wb") as f:
            f.write(raw)

        bnz_size, nzb_size = decode_file(tmp_bnz, nzb_path)
        os.remove(tmp_bnz)
        console.print(
            f"[green]✓[/] {os.path.basename(path)} -> {os.path.basename(nzb_path)}  "
            f"({_human_size(len(raw))} -> {_human_size(nzb_size)})"
        )


def cmd_verify(paths: list[str]) -> None:
    from bnz.decoder import decode, to_xml
    from bnz.encoder import parse_nzb

    all_ok = True
    for path in paths:
        bnz_path = _resolve_output(path, None, ".bnz")

        orig_size, bnz_size = encode_file(path, bnz_path)
        doc_orig = parse_nzb(path)

        with open(bnz_path, "rb") as f:
            data = f.read()
        doc_decoded = decode(data)

        failures: list[str] = []

        if len(doc_orig.files) != len(doc_decoded.files):
            failures.append(
                f"file count mismatch: {len(doc_orig.files)} != {len(doc_decoded.files)}"
            )

        if len(doc_orig.files) == 0 and len(doc_decoded.files) == 0:
            failures.append("both sides have 0 files — likely a parser bug")

        for i, (fo, fd) in enumerate(zip(doc_orig.files, doc_decoded.files)):
            if len(fo.segments) != len(fd.segments):
                failures.append(
                    f"file {i} segment count: {len(fo.segments)} != {len(fd.segments)}"
                )
            for j, (so, sd) in enumerate(zip(fo.segments, fd.segments)):
                if so.number != sd.number:
                    failures.append(
                        f"file {i} segment {j} number: {so.number} != {sd.number}"
                    )
                if so.bytes_ != sd.bytes_:
                    failures.append(
                        f"file {i} segment {j} bytes: {so.bytes_} != {sd.bytes_}"
                    )
                if so.message_id != sd.message_id:
                    failures.append(
                        f"file {i} segment {j} message_id mismatch"
                    )
                if len(failures) >= 10:
                    break
            if len(failures) >= 10:
                break

        xml_orig = to_xml(doc_orig)
        xml_decoded = to_xml(doc_decoded)
        if xml_orig != xml_decoded:
            failures.append("XML output differs")

        if not failures:
            console.print(
                f"[green]✓[/] {os.path.basename(path)}  "
                f"{_human_size(orig_size)} -> {_human_size(bnz_size)}  "
                f"({_ratio(bnz_size, orig_size)})"
            )
        else:
            console.print(f"[red]✗[/] {os.path.basename(path)} FAILED:")
            for msg in failures[:10]:
                console.print(f"  [red]- {msg}[/]")
            all_ok = False

    if all_ok:
        console.print("\n[green bold]All files verified successfully![/]")
    else:
        console.print("\n[red bold]Some files failed verification![/]")
        sys.exit(1)


def cmd_bench(paths: list[str], *, outer_gzip: bool = False) -> None:
    results: list[tuple[str, int, int, int, int]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for path in paths:
            task = progress.add_task(f"Benchmarking {os.path.basename(path)}...", total=None)
            tmp_bnz = path + ".__tmp_bench"

            t0 = time.perf_counter()
            orig_size, bnz_size = encode_file(path, tmp_bnz)
            elapsed = time.perf_counter() - t0

            if outer_gzip:
                with open(tmp_bnz, "rb") as f:
                    raw_bnz = f.read()
                bnz_gz_size = len(gzip.compress(raw_bnz, 9))
            else:
                bnz_gz_size = bnz_size

            with open(path, "rb") as f:
                nzb_gz_size = len(gzip.compress(f.read(), 9))

            os.remove(tmp_bnz)
            results.append((os.path.basename(path), orig_size, bnz_size, bnz_gz_size, nzb_gz_size))
            progress.update(task, description=f"[green]✓[/] {os.path.basename(path)} ({elapsed:.2f}s)")
            progress.remove_task(task)

    table = Table(title="BNZ Benchmark", show_lines=True)
    table.add_column("File", style="cyan", max_width=50)
    table.add_column("NZB", justify="right")
    table.add_column("BNZ", justify="right", style="green")
    if outer_gzip:
        table.add_column("BNZ.gz", justify="right", style="green bold")
    table.add_column("NZB.gz", justify="right", style="yellow")
    table.add_column("BNZ ratio", justify="right", style="green")
    if outer_gzip:
        table.add_column("BNZ.gz ratio", justify="right", style="green bold")
    table.add_column("NZB.gz ratio", justify="right", style="yellow")
    table.add_column("vs NZB.gz", justify="center")

    total_orig = 0
    total_bnz = 0
    total_bnz_gz = 0
    total_nzb_gz = 0

    for name, orig, bnz, bnz_gz, nzb_gz in results:
        total_orig += orig
        total_bnz += bnz
        total_bnz_gz += bnz_gz
        total_nzb_gz += nzb_gz

        effective = bnz_gz if outer_gzip else bnz
        bnz_wins = effective < nzb_gz
        diff = nzb_gz - effective
        winner = "[green]BNZ[/]" if bnz_wins else "[yellow]NZB.gz[/]"
        sign = "-" if bnz_wins else "+"
        style = "green" if bnz_wins else "yellow"
        badge = f"{winner} [{style}]{sign}{_human_size(abs(diff))}[/]"

        row: list[str] = [name, _human_size(orig), _human_size(bnz)]
        if outer_gzip:
            row.append(_human_size(bnz_gz))
        row.append(_human_size(nzb_gz))
        row.append(_ratio(bnz, orig))
        if outer_gzip:
            row.append(_ratio(bnz_gz, orig))
        row.append(_ratio(nzb_gz, orig))
        row.append(badge)
        table.add_row(*row)

    effective_total = total_bnz_gz if outer_gzip else total_bnz
    bnz_wins_total = effective_total < total_nzb_gz
    diff_total = total_nzb_gz - effective_total
    sign_total = "-" if bnz_wins_total else "+"
    style_total = "green" if bnz_wins_total else "yellow"
    winner_total = "[bold green]BNZ[/]" if bnz_wins_total else "[bold yellow]NZB.gz[/]"

    total_row: list[str] = [
        "[bold]TOTAL[/]",
        f"[bold]{_human_size(total_orig)}[/]",
        f"[bold]{_human_size(total_bnz)}[/]",
    ]
    if outer_gzip:
        total_row.append(f"[bold]{_human_size(total_bnz_gz)}[/]")
    total_row.append(f"[bold]{_human_size(total_nzb_gz)}[/]")
    total_row.append(f"[bold]{_ratio(total_bnz, total_orig)}[/]")
    if outer_gzip:
        total_row.append(f"[bold]{_ratio(total_bnz_gz, total_orig)}[/]")
    total_row.append(f"[bold]{_ratio(total_nzb_gz, total_orig)}[/]")
    total_row.append(
        f"{winner_total} [{style_total}]{sign_total}{_human_size(abs(diff_total))}[/]"
    )

    table.add_row(*total_row, style="on grey11")

    console.print()
    console.print(table)
    console.print()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="bnz",
        description="Binary NZB format - compress .nzb files into efficient .bnz format",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_compress = sub.add_parser("compress", aliases=["c"], help="Compress NZB to BNZ")
    p_compress.add_argument("files", nargs="+", help="NZB files to compress")
    p_compress.add_argument("-o", "--output-dir", help="Output directory for .bnz files")
    p_compress.add_argument("-z", "--gzip", action="store_true", dest="outer_gzip",
                            help="Also gzip the .bnz output (.bnz.gz)")

    p_decompress = sub.add_parser("decompress", aliases=["d"], help="Decompress BNZ to NZB")
    p_decompress.add_argument("files", nargs="+", help="BNZ files to decompress")
    p_decompress.add_argument("-o", "--output-dir", help="Output directory for .nzb files")

    p_verify = sub.add_parser("verify", aliases=["v"], help="Verify round-trip conversion")
    p_verify.add_argument("files", nargs="+", help="NZB files to verify")

    p_bench = sub.add_parser("bench", aliases=["b"], help="Benchmark BNZ vs NZB.gz")
    p_bench.add_argument("files", nargs="+", help="NZB files to benchmark")
    p_bench.add_argument("-z", "--gzip", action="store_true", dest="outer_gzip",
                         help="Also compare BNZ.gz output")

    args = parser.parse_args()

    if args.command in ("compress", "c"):
        cmd_compress(args.files, output_dir=args.output_dir, outer_gzip=args.outer_gzip)
    elif args.command in ("decompress", "d"):
        cmd_decompress(args.files, output_dir=args.output_dir)
    elif args.command in ("verify", "v"):
        cmd_verify(args.files)
    elif args.command in ("bench", "b"):
        cmd_bench(args.files, outer_gzip=args.outer_gzip)


if __name__ == "__main__":
    main()
