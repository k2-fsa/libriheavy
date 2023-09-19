#!/usr/bin/env bash

set -eou pipefail

stage=1
stop_stage=5

. ./scripts/parse_options.sh || exit 1

log() {
  local fname=${BASH_SOURCE[1]##*/}
  echo -e "$(date '+%Y-%m-%d %H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

if [ $stage -le -1 ] && [ $stop_stage -ge -1 ]; then
  log "Stage -1: Downloading audio file."
  mkdir -p download/librilight
  for subset in small medium large; do
    log "Downloading ${subset} subset."
    if [ ! -d download/librilight/${subset} ]; then
      wget -P download/librilight -c https://dl.fbaipublicfiles.com/librilight/data/${subset}.tar 
      tar xf download/librilight/${subset}.tar -C download/librilight
    else
      log "Skipping download, ${subset} subset exists."
    fi
  done
fi



if [ $stage -le 1 ] && [ $stop_stage -ge 1 ]; then
  log "Stage 1: Downloading manifests from huggingface."
  for subset in small medium large dev test_clean test_other test_clean_large test_other_large; do
    if [ ! -e libriheavy_cuts_${subset}.jsonl.gz ]; then
      log "Downloading ${subset} subset."
      wget -P raw -c https://huggingface.co/datasets/pkufool/libriheavy/resolve/main/libriheavy_cuts_${subset}.jsonl.gz
    else
      log "Skipping download, ${subset} subset exists."
    fi
  done
fi


if [ $stage -le 2 ] && [ $stop_stage -ge 2 ]; then
  for subset in small medium large test_clean test_other dev test_clean_large test_other_large; do
    log "Stage 5: Extracting subset ${subset}"
    python ./scripts/extract_and_normalize_transcript.py \
      --manifest libriheavy_cuts_${subset}.jsonl.gz \
      --subset ${subset} \
      --output-dir .
  done
fi
