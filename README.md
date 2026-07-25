# bnz

This project provides an efficient binary representation for `.nzb` files, designed to reduce storage costs and facilitate fast conversion.
Generally mostly beats naive `.nzb.gz`.

## Why?

`.bnz` uses optimized compressed binary packing instead of XML. It aims to outperform naive compression of an `.nzb` file (such as `.nzb.gz`).

## Does it Work? 
Let the numbers speak for themselves:

| File        | NZB      | BNZ      | BNZ.gz   | NZB.gz   | BNZ ratio | BNZ.gz ratio | NZB.gz ratio | vs NZB.gz       |
|-------------|----------|----------|----------|----------|-----------|--------------|--------------|-----------------|
| 623███.nzb  | 30.8 KB  | 8.4 KB   | 8.4 KB   | 9.3 KB   | 27.3%     | 27.4%        | 30.1%        | BNZ -867.0 B    |
| 934███.nzb  | 139.5 KB | 41.7 KB  | 41.7 KB  | 45.4 KB  | 29.9%     | 29.9%        | 32.6%        | BNZ -3.7 KB     |
| Aun███.nzb  | 31.5 KB  | 12.6 KB  | 12.6 KB  | 13.6 KB  | 40.0%     | 40.1%        | 43.3%        | BNZ -1.0 KB     |
| aut███.nzb  | 9.2 KB   | 3.4 KB   | 3.4 KB   | 3.8 KB   | 36.4%     | 36.6%        | 40.7%        | BNZ -382.0 B    |
| Ava███.nzb  | 491.3 KB | 122.0 KB | 122.0 KB | 120.8 KB | 24.8%     | 24.8%        | 24.6%        | NZB.gz +1.3 KB  |
| Bac███.nzb  | 624.2 KB | 57.2 KB  | 56.0 KB  | 63.5 KB  | 9.2%      | 9.0%         | 10.2%        | BNZ -7.5 KB     |
| Bac███.nzb  | 190.1 KB | 52.3 KB  | 52.3 KB  | 58.4 KB  | 27.5%     | 27.5%        | 30.7%        | BNZ -6.1 KB     |
| Bac███.nzb  | 160.5 KB | 68.4 KB  | 68.4 KB  | 74.3 KB  | 42.6%     | 42.6%        | 46.3%        | BNZ -5.9 KB     |
| Bac███.nzb  | 160.5 KB | 68.4 KB  | 68.4 KB  | 74.3 KB  | 42.6%     | 42.6%        | 46.3%        | BNZ -5.9 KB     |
| Bac███.nzb  | 670.1 KB | 61.4 KB  | 59.8 KB  | 68.0 KB  | 9.2%      | 8.9%         | 10.2%        | BNZ -8.2 KB     |
| Bac███.nzb  | 306.2 KB | 83.7 KB  | 83.7 KB  | 93.5 KB  | 27.3%     | 27.3%        | 30.5%        | BNZ -9.8 KB     |
| Che███.nzb  | 9.6 KB   | 3.7 KB   | 3.7 KB   | 4.2 KB   | 38.0%     | 38.2%        | 43.2%        | BNZ -489.0 B    |
| Clu███.nzb  | 25.4 KB  | 10.1 KB  | 10.1 KB  | 11.1 KB  | 39.8%     | 39.9%        | 43.5%        | BNZ -954.0 B    |
| Col███.nzb  | 191.5 MB | 8.0 MB   | 5.5 MB   | 11.0 MB  | 4.2%      | 2.9%         | 5.8%         | BNZ -5.6 MB     |
| Cos███.nzb  | 13.5 KB  | 5.2 KB   | 5.3 KB   | 5.9 KB   | 38.8%     | 39.0%        | 43.8%        | BNZ -666.0 B    |
| Das███.nzb  | 876.7 KB | 344.7 KB | 344.9 KB | 375.0 KB | 39.3%     | 39.3%        | 42.8%        | BNZ -30.1 KB    |
| Dea███.nzb  | 427.2 KB | 105.6 KB | 105.6 KB | 105.8 KB | 24.7%     | 24.7%        | 24.8%        | BNZ -181.0 B    |
| Der███.nzb  | 235.7 KB | 101.4 KB | 101.5 KB | 109.0 KB | 43.0%     | 43.0%        | 46.2%        | BNZ -7.5 KB     |
| Dex███.nzb  | 7.5 MB   | 283.2 KB | 54.7 KB  | 383.7 KB | 3.7%      | 0.7%         | 5.0%         | BNZ -329.0 KB   |
| Die███.nzb  | 938.1 KB | 232.5 KB | 232.3 KB | 243.0 KB | 24.8%     | 24.8%        | 25.9%        | BNZ -10.7 KB    |
| Ele███.nzb  | 38.4 KB  | 11.1 KB  | 11.1 KB  | 12.3 KB  | 28.9%     | 28.9%        | 32.0%        | BNZ -1.2 KB     |
| Fal███.nzb  | 581.7 KB | 188.3 KB | 188.4 KB | 203.5 KB | 32.4%     | 32.4%        | 35.0%        | BNZ -15.0 KB    |
| Fap███.nzb  | 11.7 MB  | 3.2 MB   | 3.2 MB   | 3.6 MB   | 27.4%     | 27.4%        | 30.7%        | BNZ -404.5 KB   |
| Fap███.nzb  | 1.3 MB   | 57.5 KB  | 30.9 KB  | 65.9 KB  | 4.3%      | 2.3%         | 5.0%         | BNZ -35.0 KB    |
| Fus███.nzb  | 648.6 KB | 280.7 KB | 280.8 KB | 302.2 KB | 43.3%     | 43.3%        | 46.6%        | BNZ -21.4 KB    |
| Gam███.nzb  | 269.6 MB | 101.4 MB | 101.5 MB | 110.5 MB | 37.6%     | 37.6%        | 41.0%        | BNZ -9.1 MB     |
| Goo███.nzb  | 229.1 KB | 70.7 KB  | 70.8 KB  | 79.5 KB  | 30.9%     | 30.9%        | 34.7%        | BNZ -8.7 KB     |
| Ina███.nzb  | 28.5 KB  | 8.0 KB   | 8.0 KB   | 8.7 KB   | 28.1%     | 28.2%        | 30.6%        | BNZ -694.0 B    |
| Ina███.nzb  | 28.2 KB  | 7.8 KB   | 7.9 KB   | 8.6 KB   | 27.8%     | 27.9%        | 30.4%        | BNZ -704.0 B    |
| Ina███.nzb  | 28.1 KB  | 7.9 KB   | 7.9 KB   | 8.6 KB   | 28.1%     | 28.2%        | 30.5%        | BNZ -673.0 B    |
| Ina███.nzb  | 28.2 KB  | 7.9 KB   | 7.9 KB   | 8.6 KB   | 27.9%     | 28.0%        | 30.4%        | BNZ -693.0 B    |
| Ina███.nzb  | 28.4 KB  | 7.9 KB   | 7.9 KB   | 8.6 KB   | 27.9%     | 27.9%        | 30.3%        | BNZ -691.0 B    |
| Ina███.nzb  | 28.3 KB  | 7.9 KB   | 7.9 KB   | 8.6 KB   | 28.0%     | 28.1%        | 30.4%        | BNZ -669.0 B    |
| Ina███.nzb  | 21.7 KB  | 6.0 KB   | 6.0 KB   | 6.6 KB   | 27.6%     | 27.7%        | 30.4%        | BNZ -597.0 B    |
| Ina███.nzb  | 27.7 KB  | 7.8 KB   | 7.8 KB   | 8.5 KB   | 28.0%     | 28.1%        | 30.5%        | BNZ -693.0 B    |
| Ina███.nzb  | 27.3 KB  | 7.7 KB   | 7.7 KB   | 8.3 KB   | 28.1%     | 28.2%        | 30.5%        | BNZ -627.0 B    |
| Ina███.nzb  | 27.6 KB  | 7.8 KB   | 7.8 KB   | 8.4 KB   | 28.0%     | 28.1%        | 30.5%        | BNZ -679.0 B    |
| Inn███.nzb  | 243.2 KB | 65.6 KB  | 65.6 KB  | 72.8 KB  | 27.0%     | 27.0%        | 29.9%        | BNZ -7.2 KB     |
| Inn███.nzb  | 243.2 KB | 65.6 KB  | 65.6 KB  | 72.8 KB  | 27.0%     | 27.0%        | 29.9%        | BNZ -7.2 KB     |
| Inn███.nzb  | 202.4 KB | 53.4 KB  | 53.4 KB  | 60.3 KB  | 26.4%     | 26.4%        | 29.8%        | BNZ -6.8 KB     |
| Inn███.nzb  | 278.0 KB | 72.8 KB  | 72.8 KB  | 82.5 KB  | 26.2%     | 26.2%        | 29.7%        | BNZ -9.7 KB     |
| Jam███.nzb  | 68.3 MB  | 16.0 MB  | 16.0 MB  | 17.5 MB  | 23.4%     | 23.4%        | 25.6%        | BNZ -1.6 MB     |
| Jap███.nzb  | 57.2 KB  | 16.4 KB  | 16.4 KB  | 18.0 KB  | 28.7%     | 28.7%        | 31.5%        | BNZ -1.6 KB     |
| Jes███.nzb  | 51.5 KB  | 15.0 KB  | 15.0 KB  | 16.6 KB  | 29.0%     | 29.1%        | 32.3%        | BNZ -1.7 KB     |
| Lum███.nzb  | 50.7 KB  | 13.6 KB  | 13.6 KB  | 14.4 KB  | 26.8%     | 26.9%        | 28.4%        | BNZ -822.0 B    |
| Min███.nzb  | 187.6 KB | 50.9 KB  | 51.0 KB  | 54.4 KB  | 27.1%     | 27.2%        | 29.0%        | BNZ -3.5 KB     |
| Nak███.nzb  | 45.7 KB  | 14.6 KB  | 14.6 KB  | 16.1 KB  | 31.9%     | 32.0%        | 35.3%        | BNZ -1.5 KB     |
| NZB███.nzb  | 3.3 MB   | 684.1 KB | 683.5 KB | 660.7 KB | 20.3%     | 20.2%        | 19.6%        | NZB.gz +22.8 KB |
| Obs███.nzb  | 814.9 KB | 360.9 KB | 361.1 KB | 386.0 KB | 44.3%     | 44.3%        | 47.4%        | BNZ -24.9 KB    |
| Oma███.nzb  | 8.4 KB   | 3.5 KB   | 3.5 KB   | 3.9 KB   | 41.0%     | 41.3%        | 45.8%        | BNZ -388.0 B    |
| Oma███.nzb  | 8.3 KB   | 3.1 KB   | 3.2 KB   | 3.5 KB   | 37.6%     | 37.9%        | 42.5%        | BNZ -391.0 B    |
| Oma███.nzb  | 7.8 KB   | 3.0 KB   | 3.0 KB   | 3.4 KB   | 38.5%     | 38.8%        | 43.3%        | BNZ -365.0 B    |
| Oma███.nzb  | 4.3 KB   | 1.5 KB   | 1.5 KB   | 1.7 KB   | 34.9%     | 35.4%        | 40.4%        | BNZ -219.0 B    |
| oma███.nzb  | 5.3 KB   | 1.7 KB   | 1.7 KB   | 2.0 KB   | 32.8%     | 33.2%        | 37.6%        | BNZ -236.0 B    |
| Onc███.nzb  | 2.5 MB   | 679.0 KB | 678.7 KB | 754.9 KB | 26.6%     | 26.6%        | 29.6%        | BNZ -76.2 KB    |
| Pos███.nzb  | 12.0 KB  | 4.7 KB   | 4.8 KB   | 5.3 KB   | 39.3%     | 39.5%        | 43.8%        | BNZ -527.0 B    |
| Rat███.nzb  | 826.4 KB | 330.3 KB | 330.4 KB | 359.0 KB | 40.0%     | 40.0%        | 43.4%        | BNZ -28.6 KB    |
| Rea███.nzb… | 11.7 MB  | 3.2 MB   | 3.2 MB   | 3.6 MB   | 27.6%     | 27.6%        | 30.4%        | BNZ -337.1 KB   |
| Rea███.nzb… | 11.9 MB  | 3.3 MB   | 3.3 MB   | 3.7 MB   | 27.4%     | 27.4%        | 30.8%        | BNZ -407.9 KB   |
| Sca███.nzb  | 214.6 KB | 92.7 KB  | 92.8 KB  | 99.9 KB  | 43.2%     | 43.2%        | 46.6%        | BNZ -7.1 KB     |
| Sca███.nzb  | 220.8 KB | 94.3 KB  | 94.3 KB  | 102.1 KB | 42.7%     | 42.7%        | 46.2%        | BNZ -7.8 KB     |
| Sca███.nzb  | 194.5 KB | 81.2 KB  | 81.2 KB  | 88.3 KB  | 41.8%     | 41.8%        | 45.4%        | BNZ -7.0 KB     |
| Sca███.nzb  | 238.7 KB | 106.3 KB | 106.3 KB | 113.5 KB | 44.5%     | 44.5%        | 47.5%        | BNZ -7.1 KB     |
| Sca███.nzb  | 153.3 KB | 62.8 KB  | 62.8 KB  | 68.0 KB  | 40.9%     | 40.9%        | 44.4%        | BNZ -5.2 KB     |
| Sca███.nzb  | 700.9 KB | 293.7 KB | 293.8 KB | 317.6 KB | 41.9%     | 41.9%        | 45.3%        | BNZ -23.8 KB    |
| SD_███.nzb  | 1.4 MB   | 390.8 KB | 390.9 KB | 418.1 KB | 27.0%     | 27.0%        | 28.9%        | BNZ -27.2 KB    |
| SD_███.nzb  | 3.2 MB   | 871.8 KB | 872.1 KB | 943.8 KB | 26.7%     | 26.7%        | 28.9%        | BNZ -71.7 KB    |
| SD_███.nzb  | 1.4 MB   | 358.6 KB | 358.7 KB | 392.7 KB | 25.9%     | 25.9%        | 28.4%        | BNZ -34.0 KB    |
| Sea███.nzb  | 1.3 MB   | 529.8 KB | 530.0 KB | 570.4 KB | 40.9%     | 40.9%        | 44.0%        | BNZ -40.5 KB    |
| Spr███.nzb  | 177.9 KB | 45.7 KB  | 45.7 KB  | 45.1 KB  | 25.7%     | 25.7%        | 25.3%        | NZB.gz +682.0 B |
| The███.nzb  | 31.6 KB  | 8.1 KB   | 8.1 KB   | 9.0 KB   | 25.7%     | 25.8%        | 28.4%        | BNZ -855.0 B    |
| The███.nzb  | 29.7 KB  | 8.0 KB   | 8.0 KB   | 8.7 KB   | 26.9%     | 26.9%        | 29.5%        | BNZ -767.0 B    |
| The███.nzb  | 29.5 KB  | 8.0 KB   | 8.0 KB   | 8.8 KB   | 27.0%     | 27.0%        | 29.6%        | BNZ -784.0 B    |
| The███.nzb  | 29.5 KB  | 8.0 KB   | 8.0 KB   | 8.8 KB   | 27.0%     | 27.0%        | 29.6%        | BNZ -784.0 B    |
| the███.nzb  | 436.5 KB | 175.3 KB | 175.4 KB | 190.0 KB | 40.2%     | 40.2%        | 43.5%        | BNZ -14.6 KB    |
| The███.nzb  | 247.1 KB | 68.2 KB  | 68.3 KB  | 73.3 KB  | 27.6%     | 27.6%        | 29.7%        | BNZ -5.1 KB     |
| The███.nzb  | 250.4 KB | 58.2 KB  | 58.2 KB  | 59.7 KB  | 23.3%     | 23.2%        | 23.9%        | BNZ -1.6 KB     |
| The███.nzb  | 246.7 KB | 68.1 KB  | 68.2 KB  | 73.1 KB  | 27.6%     | 27.6%        | 29.6%        | BNZ -4.9 KB     |
| The███.nzb  | 246.9 KB | 68.2 KB  | 68.3 KB  | 73.3 KB  | 27.6%     | 27.6%        | 29.7%        | BNZ -5.0 KB     |
| The███.nzb  | 284.9 KB | 71.9 KB  | 71.8 KB  | 74.4 KB  | 25.2%     | 25.2%        | 26.1%        | BNZ -2.6 KB     |
| The███.nzb  | 395.7 KB | 169.0 KB | 169.1 KB | 179.2 KB | 42.7%     | 42.7%        | 45.3%        | BNZ -10.1 KB    |
| The███.nzb  | 196.4 KB | 61.9 KB  | 62.0 KB  | 68.2 KB  | 31.5%     | 31.5%        | 34.7%        | BNZ -6.3 KB     |
| The███.nzb  | 316.9 KB | 87.4 KB  | 87.4 KB  | 94.1 KB  | 27.6%     | 27.6%        | 29.7%        | BNZ -6.7 KB     |
| The███.nzb  | 2.0 MB   | 827.1 KB | 827.4 KB | 903.7 KB | 40.2%     | 40.2%        | 43.9%        | BNZ -76.3 KB    |
| Tin███.nzb  | 11.6 MB  | 3.2 MB   | 3.2 MB   | 3.6 MB   | 27.5%     | 27.6%        | 30.8%        | BNZ -388.0 KB   |
| Tou███.nzb  | 861.8 KB | 364.4 KB | 364.6 KB | 385.9 KB | 42.3%     | 42.3%        | 44.8%        | BNZ -21.4 KB    |
| WtF███.nzb  | 588.0 B  | 202.0 B  | 225.0 B  | 430.0 B  | 34.4%     | 38.3%        | 73.1%        | BNZ -205.0 B    |
| Zim███.nzb  | 356.8 KB | 160.3 KB | 160.4 KB | 172.1 KB | 44.9%     | 45.0%        | 48.2%        | BNZ -11.7 KB    |
| Zor███.nzb  | 31.7 KB  | 8.6 KB   | 8.6 KB   | 9.4 KB   | 27.0%     | 27.0%        | 29.6%        | BNZ -827.0 B    |
| Zor███.nzb  | 27.4 KB  | 8.8 KB   | 8.8 KB   | 9.5 KB   | 31.9%     | 32.0%        | 34.8%        | BNZ -772.0 B    |
| Zor███.nzb  | 20.2 KB  | 5.7 KB   | 5.7 KB   | 6.3 KB   | 28.3%     | 28.4%        | 31.2%        | BNZ -588.0 B    |
| Zor███.nzb  | 27.4 KB  | 7.6 KB   | 7.7 KB   | 8.6 KB   | 27.9%     | 28.0%        | 31.3%        | BNZ -937.0 B    |
| TOTAL       | 615.9 MB | 148.1 MB | 145.3 MB | 164.0 MB | 24.0%     | 23.6%        | 26.6%        | BNZ -18.7 MB    |

Except for 3 `.nzb` files, bnz always takes the win saving multiple MB in larger files for overall savings of 21MB over `.nzb.gz` on this 93 `.nzb` file benchmark. 

Best result by ratio: 7.5MB → 54.7KB

Worst result vs `nzb.gz`: 3.3MB → 683.5KB (Worse by 22.8KB compared to `nzb.gz`)

## Requirements

- Python
- uv (recommended for environment management)

## Installation

```bash
uv pip install .
```

## Usage

The `bnz` CLI tool supports the following commands:

### Compress
Compress one or more `.nzb` files to `.bnz`:
```bash
bnz compress <file1.nzb> [file2.nzb ...]
```
Options:
- `-o, --output-dir`: Specify an output directory.
- `-z, --gzip`: Also gzip the output to `.bnz.gz`.

### Decompress
Decompress one or more `.bnz` files back to `.nzb`:
```bash
bnz decompress <file1.bnz> [file2.bnz ...]
```
Options:
- `-o, --output-dir`: Specify an output directory.

### Verify
Verify round-trip conversion for one or more files:
```bash
bnz verify <file1.nzb> [file2.nzb ...]
```

### Benchmark
Benchmark BNZ against compressed NZB files:
```bash
bnz bench <file1.nzb> [file2.nzb ...]
```
Options:
- `-z, --gzip`: Also compare `.bnz.gz` output. Use this for best results!

## Project Structure

```text
.
├── src/bnz/
│   ├── __init__.py
│   ├── cli.py       # CLI implementation
│   ├── decoder.py   # BNZ to NZB logic
│   ├── encoder.py   # NZB to BNZ logic
│   └── varint.py    # Variable integer encoding/decoding
├── pyproject.toml
├── uv.lock
└── README.md
```