import argparse
import gzip
import json
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
        "--output-dir",
        type=Path,
        help="""The dir that the wav.scp, text and segments to write to.
        """
    )
    return parser.parse_args()


def normalize(s : str) -> str:
    s = s.replace("‘", "'")
    s = s.replace("’", "'")
    tokens = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'")
    s_list = [x.upper() if x in tokens else " " for x in s]
    s = " ".join("".join(s_list).split()).strip()
    return s


def main():
    args = get_args()
    ifile = args.manifest
    assert ifile.is_file(), f"File not exists : {ifile}"
    assert str(ifile).endswith("jsonl.gz"), f"Expect a jsonl gz file, given : {ifile}"
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    wav_scp = {}
    texts = {}
    segments = {}
    with gzip.open(ifile, "r") as f:
        for line in f:
            cut = json.loads(line)
            seg_id = cut["id"]
            start = math.floor(1000 * cut["start"]) / 1000
            duration = math.floor(1000 * cut["duration"]) / 1000
            wav_id = cut["recording"]["id"]
            wav = cut["recording"]["sources"][0]["source"]
            wav = wav.replace("/star-kw/data/libri-light", "download/librilight")
            text = cut["supervisions"][0]["custom"]["texts"][0]
            text = normalize(text)
            wav_scp[wav_id] = wav
            texts[seg_id] = text
            segments[seg_id] = (wav_id, start, start + duration)

    with open(output_dir/"wav.scp", "w", encoding="utf8") as f:
        for k, v in wav_scp.items():
            f.write(f"{k} {v}\n")
    with open(output_dir/"text", "w", encoding="utf8") as f:
        for k, v in texts.items():
            f.write(f"{k} {v}\n")
    with open(output_dir/"segments", "w", encoding="utf8") as f:
        for k, v in segments.items():
            f.write(f"{k} {v[0]} {v[1]} {v[2]}\n")

if __name__ == "__main__":
    main()
    
