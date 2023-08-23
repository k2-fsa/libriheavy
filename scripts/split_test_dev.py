import argparse
import editdistance
import gzip
import json
import logging
import math
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="""The dir to write the result.
        """,
    )

    parser.add_argument(
        "manifests",
        type=Path,
        nargs="+",
        help="The manifests to be processed, normally the subsets of a corpus.",
    )

    return parser.parse_args()


def get_book_speaker_duration(manifests: List[Path], output_dir: Path):
    book_duration = {}
    speaker_duration = {}
    book_speaker_duration = {}
    for file in manifests:
        with gzip.open(file, "r") as fin:
            for line in fin:
                line = json.loads(line)
                speaker = line["id"].split("/")[1]
                book = line["custom"]["text_path"].split("/")[-2]
                duration = line["duration"]

                if speaker in speaker_duration:
                    speaker_duration[speaker] += duration
                else:
                    speaker_duration[speaker] = duration

                if book in book_duration:
                    book_duration[book] += duration
                else:
                    book_duration[book] = duration

                if (speaker, book) in book_speaker_duration:
                    book_speaker_duration[(speaker, book)] += duration
                else:
                    book_speaker_duration[(speaker, book)] = duration
    in_dir = manifests[0].parent
    with open(in_dir / "speaker.dur", "w") as f:
        json.dump(speaker_duration, f, indent=4)
    with open(in_dir / "book.dur", "w") as f:
        json.dump(book_duration, f, indent=4)
    with open(in_dir / "book_speaker.dur", "w") as f:
        json.dump(book_speaker_duration, f, indent=4)


def select_books_speakers(manifests: List[Path], output_dir: Path):
    in_dir = manifests[0].parent
    if (
        not (in_dir / "speaker.dur").exists()
        or not (in_dir / "book.dur").exists()
        or not (in_dir / "book_speaker.dur").exists()
    ):
        get_book_speaker_duration(manifests, output_dir)
    with open(in_dir / "speaker.dur", "r") as f:
        speaker_duration = json.load(f)
    with open(in_dir / "book.dur", "r") as f:
        book_duration = json.load(f)
    with open(in_dir / "book_speaker.dur", "r") as f:
        book_speaker_duration = json.load(f)

    selected_books = set()
    selected_speakers = set()
    selected_duration = 0.0
    for sb, d in book_speaker_duration.items():
        s_duration = speaker_duration[sb[0]]
        b_duration = book_duration[sb[1]]
        s_rate = d / s_duration
        b_rate = d / b_duration
        if (
            s_duration < 3600 * 6
            and b_duration < 3600 * 6
            and b_rate >= 0.5
            and s_rate >= 0.5
        ):
            selected_speakers.add(sb[0])
            selected_books.add(sb[1])
            selected_duration += d
    logging.info(
        f"Selected {len(selected_books)} books, {len(selected_speakers)} speakers."
    )
    logging.info(f"Selected duration : {selected_duration / 3600:.2f} hours.")
    with open(output_dir / "selected_books.txt", "w") as f:
        for x in selected_books:
            f.write(x + "\n")
    with open(output_dir / "selected_speakers.txt", "w") as f:
        for x in selected_speakers:
            f.write(x + "\n")


def split_test_set(manifests: List[Path], output_dir: Path):
    if (
        not (output_dir / "selected_speakers.txt").exists()
        or not (output_dir / "selected_books.txt").exists()
    ):
        select_books_speakers(manifests, output_dir)
    selected_speakers = set()
    with open(output_dir / "selected_speakers.txt", "r") as f:
        for line in f:
            selected_speakers.add(line.strip())
    selected_books = set()
    with open(output_dir / "selected_books.txt", "r") as f:
        for line in f:
            selected_books.add(line.strip())

    tfile = gzip.open(output_dir / "libriheavy_test_raw.jsonl.gz", "w")

    for m in manifests:
        with gzip.open(output_dir / m.name, "w") as f:
            with gzip.open(m, "r") as fin:
                for line in fin:
                    line = json.loads(lines)
                    speaker = line["id"].split("/")[1]
                    book = line["custom"]["text_path"].split("/")[-2]
                    if book in selected_books or speaker in selected_speakers:
                        tfile.write(lines)
                    else:
                        f.write(lines)
    tfile.close()


def main():
    args = get_args()
    manifests = args.manifests
    in_dir = manifests[0].parent

    for m in manifests:
        assert (
            m.parent == in_dir
        ), f"Input manifests MUST be in the same directory, given : {(m.parent, in_dir)}."
        assert str(m).endswith(
            "jsonl.gz"
        ), "The raw manifest is expected to be a jsonl.gz file."
    assert (
        args.output_dir != in_dir
    ), f"Manifests directory MUST not be the same as the output_dir, given : {(args.output_dir, in_dir)}."

    args.output_dir.mkdir(parents=True, exist_ok=True)
    split_test_set(args.manifests, args.output_dir)


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)
    main()
