import argparse
import editdistance
import gzip
import json
import logging
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        help="""The manifest to be filtered.
        """,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="""The dir to write the result.
        """,
    )

    parser.add_argument(
        "--cer-threthod",
        type=float,
        default=0.05,
        help="""Through the cuts that have cer greater than this value""",
    )

    return parser.parse_args()


def normalize(s: str) -> str:
    s = s.replace("‘", "'")
    s = s.replace("’", "'")
    tokens = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'")
    s_list = [x.upper() if x in tokens else " " for x in s]
    s = " ".join("".join(s_list).split()).strip()
    return s


def filter(
    manifest,
    cer_threthod: float,
    output_dir: Path,
):
    name = manifest.name.replace(".jsonl.gz", "") + "_filter.jsonl.gz"
    of = gzip.open(output_dir / name, "w")
    with gzip.open(manifest, "r") as fin:
        for line in fin:
            cut = json.loads(line)
            texts = cut["supervisions"][0]["custom"]["texts"]
            ref = normalize(texts[0]).strip()
            hyp = texts[1].strip()
            distance = editdistance.eval(ref, hyp)
            cer = distance / len(ref)
            if cer <= cer_threthod:
                of.write(line)
    of.close()


def main():
    args = get_args()
    manifest = args.manifest
    assert manifest.is_file(), f"File not exists : {manifest}"
    assert str(manifest).endswith(
        "jsonl.gz"
    ), "The manifest is expected to be a jsonl.gz file, given : {manifest}"

    args.output_dir.mkdir(parents=True, exist_ok=True)

    filter(manifest, cer_threthod=args.cer_threthod, output_dir=args.output_dir)


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)
    main()
