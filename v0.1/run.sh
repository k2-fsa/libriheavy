#!/usr/bin/env bash

set -eou pipefail

stage=1
stop_stage=5

. ../scripts/parse_options.sh || exit 1

log() {
  # This function is from espnet
  local fname=${BASH_SOURCE[1]##*/}
  echo -e "$(date '+%Y-%m-%d %H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

if [ $stage -le 1 ] && [ $stop_stage -ge 1 ]; then
  mkdir -p raw
  for subset in small medium large; do
    if [ ! -e raw/libriheavy_cuts_${subset}.jsonl.gz ]; then
      log "Downloading ${subset} subset."
      wget -P raw -c https://huggingface.co/datasets/pkufool/libriheavy/resolve/main/v0.1/raw/libriheavy_cuts_${subset}.jsonl.gZ
    else
      log "Skipping download, ${subset} subset exists."
    fi
  done
fi

if [ $stage -le 2 ] && [ $stop_stage -ge 2 ]; then
  for subset in small medium large; do
    if [ ! -e raw/.${subset}_filter.done ]; then
      log "Filtering ${subset} subset."
      # might be symbolic link
      rm raw/libriheavy_cuts_${subset}_filter.jsonl.gz
      python ../scripts/filter_by_wers.py --manifest raw/libriheavy_cuts_${subset}.jsonl.gz
      touch raw/.${subset}_filter.done
    fi
  done
else
  for subset in small medium large; do
    ln -s raw/libriheavy_cuts_${subset}.jsonl.gz raw/libriheavy_cuts_${subset}_filter.jsonl.gz
  done
fi

if [ $stage -le 3 ] && [ $stop_stage -ge 3 ]; then
  python split_test_dev.py
fi


