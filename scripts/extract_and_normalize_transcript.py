import argparse
import gzip
import json
import logging
import math
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        help="""The manifest to extract the wav.scp, text and segments, MUST be
        a jsonl.gz file.
        """,
    )
    parser.add_argument(
        "--subset",
        type=str,
        help="The subset of the corpus, could be small, medium or large.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="""The dir that the wav.scp, text and segments to write to.
        """,
    )
    return parser.parse_args()


def normalize_text(s: str) -> str:
    s = s.replace("‘", "'")
    s = s.replace("’", "'")
    tokens = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'")
    s_list = [x.upper() if x in tokens else " " for x in s]
    s = " ".join("".join(s_list).split()).strip()
    return s


def clean_text(s: str) -> str:
    table = str.maketrans("’‘，。；？！（）：-《》、“”【】", "'',.;?!(): <>/\"\"[]")
    s = s.translate(table)
    return s.strip()


def write_kaldi(ifile: Path, subset: str, output_dir: Path):
    no_punc_dir = output_dir / "upper_no_punc" / "kaldi" / subset
    punc_dir = output_dir / "cases_and_punc" / "kaldi" / subset
    no_punc_dir.mkdir(parents=True, exist_ok=True)
    punc_dir.mkdir(parents=True, exist_ok=True)

    wav_scp = {}
    texts = {}
    punc_texts = {}
    segments = {}
    with gzip.open(ifile, "r") as f:
        for line in f:
            cut = json.loads(line)
            seg_id = cut["id"]
            start = math.floor(1000 * cut["start"]) / 1000
            duration = math.floor(1000 * cut["duration"]) / 1000
            wav_id = cut["recording"]["id"]
            wav = cut["recording"]["sources"][0]["source"]
            text = cut["supervisions"][0]["custom"]["texts"][0]
            no_punc_text = normalize_text(text)
            punc_text = clean_text(text)
            wav_scp[wav_id] = wav
            texts[seg_id] = no_punc_text
            punc_texts[seg_id] = punc_text
            segments[seg_id] = (wav_id, start, start + duration)

    with open(punc_dir / "wav.scp", "w", encoding="utf8") as f1, open(
        no_punc_dir / "wav.scp", "w", encoding="utf8"
    ) as f2:
        for k, v in wav_scp.items():
            f1.write(f"{k} {v}\n")
            f2.write(f"{k} {v}\n")
    with open(punc_dir / "segments", "w", encoding="utf8") as f1, open(
        no_punc_dir / "segments", "w", encoding="utf8"
    ) as f2:
        for k, v in segments.items():
            f1.write(f"{k} {v[0]} {v[1]} {v[2]}\n")
            f2.write(f"{k} {v[0]} {v[1]} {v[2]}\n")
    with open(punc_dir / "text", "w", encoding="utf8") as f:
        for k, v in punc_texts.items():
            f.write(f"{k} {v}\n")
    with open(no_punc_dir / "text", "w", encoding="utf8") as f:
        for k, v in texts.items():
            f.write(f"{k} {v}\n")


def write_lhotse(ifile: Path, output_dir: Path):
    no_punc_dir = output_dir / "upper_no_punc" / "lhotse"
    punc_dir = output_dir / "cases_and_punc" / "lhotse"
    no_punc_dir.mkdir(parents=True, exist_ok=True)
    punc_dir.mkdir(parents=True, exist_ok=True)

    with gzip.open(no_punc_dir / ifile.name, "w") as f1, gzip.open(
        punc_dir / ifile.name, "w"
    ) as f2, gzip.open(ifile, "r") as fin:
        for line in fin:
            cut = json.loads(line)
            text = cut["supervisions"][0]["custom"]["texts"][0]
            del cut["supervisions"][0]["custom"]
            del cut["custom"]
            no_punc_text = normalize_text(text)
            punc_text = clean_text(text)
            cut["supervisions"][0]["text"] = no_punc_text
            f1.write((json.dumps(cut) + "\n").encode())
            cut["supervisions"][0]["text"] = punc_text
            f2.write((json.dumps(cut) + "\n").encode())


def main():
    args = get_args()
    ifile = args.manifest
    assert ifile.is_file(), f"File not exists : {ifile}"
    assert str(ifile).endswith("jsonl.gz"), f"Expect a jsonl gz file, given : {ifile}"
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    write_kaldi(ifile, subset=args.subset, output_dir=output_dir)
    write_lhotse(ifile, output_dir=output_dir)


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)
    main()
