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
        "--raw",
        type=Path,
        help="""The raw test dev subset split from the whole set.
        """,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="""The dir to write the result.
        """,
    )

    parser.add_argument(
        "--wer-threthod",
        type=float,
        default=0.15,
        help="""Through the cuts that have wer greater than this value""",
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=10,
        help="""The number of hours for eash subset (test-clean, test-other).""",
    )

    return parser.parse_args()


def normalize(s: str) -> str:
    s = s.replace("‘", "'")
    s = s.replace("’", "'")
    tokens = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'")
    s_list = [x.upper() if x in tokens else " " for x in s]
    s = " ".join("".join(s_list).split()).strip()
    return s


def get_speaker_wers(raw_manifest: str) -> Dict[str, float]:
    speaker_wers = {}
    with gzip.open(raw_manifest, "r") as fin:
        for line in fin:
            cut = json.loads(line)
            speaker = cut["id"].split("/")[1]
            texts = cut["supervisions"][0]["custom"]["texts"]
            ref = normalize(texts[0]).split()
            hyp = texts[1].split()
            distance = editdistance.eval(ref, hyp)
            if speaker in speaker_wers:
                speaker_wers[speaker]["errs"] += distance
                speaker_wers[speaker]["len"] += len(ref)
            else:
                speaker_wers[speaker] = {}
                speaker_wers[speaker]["errs"] = distance
                speaker_wers[speaker]["len"] = len(ref)
    speaker_wers = {k: v["errs"] / v["len"] for k, v in speaker_wers.items()}
    return speaker_wers


def split_subset(
    raw_manifest,
    wer_threthod: float,
    hours: int,
    speaker_wers: List[Tuple[str, float]],
    output_dir: Path,
):
    speaker_wers = sorted(speaker_wers.items(), key=lambda x: x[1])
    clean_speakers = set([x[0] for x in speaker_wers[0 : len(speaker_wers) // 2]])
    other_speakers = set([x[0] for x in speaker_wers[len(speaker_wers) // 2 :]])
    clean_hours = 0
    other_hours = 0
    with gzip.open(raw_manifest, "r") as fin:
        for line in fin:
            cut = json.loads(line)
            speaker = cut["id"].split("/")[1]
            texts = cut["supervisions"][0]["custom"]["texts"]
            duration = math.floor(1000 * cut["duration"]) / 1000
            ref = normalize(texts[0]).split()
            hyp = texts[1].split()
            distance = editdistance.eval(ref, hyp)
            wer = distance / len(ref)
            if wer >= wer_threthod:
                continue
            else:
                if speaker in clean_speakers:
                    clean_hours += duration
                else:
                    assert speaker in other_speakers, speaker
                    other_hours += duration

    clean_hours = math.floor(clean_hours / 3600 * 1000) / 1000
    other_hours = math.floor(other_hours / 3600 * 1000) / 1000

    logging.info(f"clean hours : {clean_hours}, other hours : {other_hours}")
    clean_prob = hours * 2 / clean_hours
    other_prob = hours * 2 / other_hours

    clean_of = gzip.open(output_dir / "libriheavy_test_clean.jsonl.gz", "w")
    clean_large_of = gzip.open(output_dir / "libriheavy_test_clean_large.jsonl.gz", "w")
    other_of = gzip.open(output_dir / "libriheavy_test_other.jsonl.gz", "w")
    other_large_of = gzip.open(output_dir / "libriheavy_test_other_large.jsonl.gz", "w")
    dev_of = gzip.open(output_dir / "libriheavy_dev.jsonl.gz", "w")

    with gzip.open(raw_manifest, "r") as fin:
        for line in fin:
            cut = json.loads(line)
            speaker = cut["id"].split("/")[1]
            prob = random.random()
            if speaker in clean_speakers:
                if prob <= clean_prob:
                    if random.random() >= 0.5:
                        dev_of.write(line)
                    else:
                        clean_of.write(line)
                else:
                    clean_large_of.write(line)
            else:
                assert speaker in other_speakers, speaker
                if prob <= other_prob:
                    if random.random() >= 0.5:
                        dev_of.write(line)
                    else:
                        other_of.write(line)
                else:
                    other_large_of.write(line)
    clean_of.close()
    clean_large_of.close()
    other_of.close()
    other_large_of.close()
    dev_of.close()


def main():
    args = get_args()
    raw_manifest = args.raw
    assert raw_manifest.is_file(), f"File not exists : {raw_manifest}"
    assert str(raw_manifest).endswith(
        "jsonl.gz"
    ), "The raw manifest is expected to be a jsonl.gz file."

    args.output_dir.mkdir(parents=True, exist_ok=True)

    speaker_wers = get_speaker_wers(raw_manifest)
    split_subset(
        raw_manifest,
        wer_threthod=args.wer_threthod,
        hours=args.hours,
        speaker_wers=speaker_wers,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)
    main()
