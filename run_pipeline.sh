#!/usr/bin/env bash

set -eou pipefail

stage=1
stop_stage=5

. ./scripts/parse_options.sh || exit 1

log() {
  local fname=${BASH_SOURCE[1]##*/}
  echo -e "$(date '+%Y-%m-%d %H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}


if [ $stage -le 0 ] && [ $stop_stage -ge 0 ]; then
  log "Stage 1: Downloading raw manifests from modelscope."
  if [ ! -e raw/libriheavy_cuts_small.jsonl.gz ]; then
    GIT_LFS_SKIP_SMUDGE=1 git clone https://www.modelscope.cn/datasets/pkufool/Libriheavy.git
    cd Libriheavy
    git lfs pull --include "raw/*.jsonl.gz"
    mv raw ../
    cd ..
    rm -rf Libriheavy
  fi
fi


if [ $stage -le 1 ] && [ $stop_stage -ge 1 ]; then
  log "Stage 1: Downloading raw manifest aligned by text_search project."
  mkdir -p raw
  for subset in small medium large; do
    if [ ! -e raw/libriheavy_cuts_${subset}.jsonl.gz ]; then
      log "Downloading ${subset} subset."
      wget -P raw -c https://huggingface.co/datasets/pkufool/libriheavy/resolve/main/raw/libriheavy_cuts_${subset}.jsonl.gz
    else
      log "Skipping download, ${subset} subset exists."
    fi
  done
fi


if [ $stage -le 2 ] && [ $stop_stage -ge 2 ]; then
  log "Stage 2: Filtering cuts with high cer."
  for subset in small medium large; do
    if [ ! -e raw/.${subset}_filter.done ]; then
      log "Filtering ${subset} subset."
      # might be symbolic link
      rm raw/libriheavy_cuts_${subset}_filter.jsonl.gz
      python ./scripts/filter_by_wers.py --manifest raw/libriheavy_cuts_${subset}.jsonl.gz
      touch raw/.${subset}_filter.done
    fi
  done
else
  for subset in small medium large; do
    if [ ! -e raw/.${subset}_filter.done ]; then
      rm raw/libriheavy_cuts_${subset}_filter.jsonl.gz
      ln -s raw/libriheavy_cuts_${subset}.jsonl.gz raw/libriheavy_cuts_${subset}_filter.jsonl.gz
    fi
  done
fi


if [ $stage -le 3 ] && [ $stop_stage -ge 3 ]; then
  log "Stage 3: Excluding test and dev cuts from training set."
  python ./scripts/split_test_dev.py --output-dir . \
    raw/libriheavy_cuts_small.jsonl.gz \
    raw/libriheavy_cuts_medium.jsonl.gz \
    raw/libriheavy_cuts_large.jsonl.gz
fi


if [ $stage -le 4 ] && [ $stop_stage -ge 4 ]; then
  log "Stage 4: Splitting test and dev sets."
  python ./scripts/process_test_dev.py --raw libriheavy_cuts_test_raw.jsonl.gz \
    --output-dir .
fi
