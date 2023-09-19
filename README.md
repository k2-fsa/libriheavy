# Libriheavy: a 50,000 hours ASR corpus with punctuation casing and context

This is the official repository of the Libriheavy dataset. Please refer to our paper: *Libriheavy: a 50,000 hours ASR corpus with punctuation casing and context* for more details. [Preprint available on arxiv](https://arxiv.org/abs/2309.08105).

## How to download the dataset

The audio files of Libriheavy is the same as those in Librilight, the audio files is available [here](https://github.com/facebookresearch/libri-light/tree/main/data_preparation), you can download it by:

```
bash run.sh --stage -1 --stop-stage -1
```

The manifests of Libriheavy is hosted in [huggingface](https://huggingface.co/datasets/pkufool/libriheavy) and [modelscope](https://www.modelscope.cn/datasets/pkufool/Libriheavy/summary)(for users in Chinese mainland). You can download the manifests via:

From huggingface:

```
bash run.sh --stage 1 --stop-stage 1
```

From modelscope:
```
bash run.sh --stage 0 --stop-stage 0
```

The manifest downloaded above looks like follows, we have two version of `texts` and `pre_texts`, the first item is the transcript from original book(with casing and punctuation), the second item is the decoding result from a asr model. The second item was used to align the transcript in the original book, we decide to keep it.

```json
{
  "id": "small/100/sea_fairies_0812_librivox_64kb_mp3/01_baum_sea_fairies_64kb_0",
  "start": 243.919,
  "duration": 7.36,
  "channel": 0,
  "supervisions": [
    {
      "id": "small/100/sea_fairies_0812_librivox_64kb_mp3/01_baum_sea_fairies_64kb_0",
      "recording_id": "small/100/sea_fairies_0812_librivox_64kb_mp3/01_baum_sea_fairies_64kb",
      "start": 0,
      "duration": 7.36,
      "channel": 0,
      "language": "English",
      "speaker": "100",
      "custom": {
        "texts": [
          "The little girl was thoughtful for a moment. \"But why do folks dive in the water when the mermaids smile an' wink?\" she asked.",
          "THE LITTLE GIRL WAS THOUGHTFUL FOR A MOMENT BUT WHY DO FOLKS DIVE IN THE WATER WHEN THE MERMAIDS SMILE AND WINK SHE ASKED"
        ],
        "pre_texts": [                                                                                                                      
          "...us mortal folk,\" replied Cap'n Bill. \"But if anyone happens to see 'em, what then, Cap'n?\" \"Then,\" he answered, slowly wagging his head, \"the mermais give 'em a smile an' a wink, an' they dive into the water an' gets drownded.\" \"S'pose they knew how to swim, Cap'n Bill?\" \"That don't make any diff'rence, Trot. The mermaids live deep down, an' the poor mortals never come up again.",
          "...US MORTAL FOLK REPLIED CAP'N BILL BUT IF ANYONE HAPPENS TO SEE EM WHAT THEN CAP'N THEN HE ANSWERED SLOWLY WAGGING HIS HEAD THE MERMAIDS GIVE EM A SMILE AND A WINK AND THEY DIVES INTO THE WATER AND GETS DROWNDED S'POSE THEY KNOW HOW TO SWIM CAP'N BILL THAT DON'T MAKE ANY DIFFERENCE TROT THE MERMAIDS LIVE DEEP DOWN AND THE POOR MORTALS NEVER COME UP AGAIN"
        ],
        "begin_byte": 4993,
        "end_byte": 5120
      }
    }
  ],
  "recording": {
    "id": "small/100/sea_fairies_0812_librivox_64kb_mp3/01_baum_sea_fairies_64kb",
    "sources": [
      {
        "type": "file",
        "channels": [
          0
        ],
        "source": "download/librilight/small/100/sea_fairies_0812_librivox_64kb_mp3/01_baum_sea_fairies_64kb.flac"
      }
    ],
    "sampling_rate": 16000,
    "num_samples": 9567080,
    "duration": 597.942,
    "channel_ids": [
      0
    ]
  },
  "custom": {
    "text_path": "download/librilight_text/output_text_small_cleaned/Sea Fairies/text.txt"
  },
  "type": "MonoCut"
}
```

This is the full version of Libriheavy which can be use for various speech tasks.
You can further extract the manifests for pure ASR model training purpose by:

```
bash run.sh --stage 2 --stop-stage 2
```

Now, you have k2 format(lhotse cuts) and kaldi format corpus for both normalized version(upper case without punctuation) and full formated version(casing with punctuation):

```
├── cases_and_punc
│   ├── kaldi
│   │   ├── large
│   │   │   ├── segments
│   │   │   ├── text
│   │   │   └── wav.scp
......
│   │   ├── test_clean
│   │   │   ├── segments
│   │   │   ├── text
│   │   │   └── wav.scp
│   └── lhotse
│       ├── libriheavy_cuts_dev.jsonl.gz
│       ├── libriheavy_cuts_large.jsonl.gz
│       ├── libriheavy_cuts_medium.jsonl.gz
│       ├── libriheavy_cuts_small.jsonl.gz
│       ├── libriheavy_cuts_test_clean.jsonl.gz
│       ├── libriheavy_cuts_test_clean_large.jsonl.gz
│       ├── libriheavy_cuts_test_other.jsonl.gz
│       └──  libriheavy_cuts_test_other_large.jsonl.gz
└── upper_no_punc
    ├── kaldi
    │   ├── large
    │   │   ├── segments
    │   │   ├── text
    │   │   └── wav.scp
    ......
    │   ├── test_other
    │   │   ├── segments
    │   │   ├── text
    │   │   └── wav.scp
    └── lhotse
        ├── libriheavy_cuts_dev.jsonl.gz
        ├── libriheavy_cuts_large.jsonl.gz
        ├── libriheavy_cuts_medium.jsonl.gz
        ├── libriheavy_cuts_small.jsonl.gz
        ├── libriheavy_cuts_test_clean.jsonl.gz
        ├── libriheavy_cuts_test_clean_large.jsonl.gz
        ├── libriheavy_cuts_test_other.jsonl.gz
        └── libriheavy_cuts_test_other_large.jsonl.gz
```

> For how to use the `pre_texts`, we have a paper: *PromptASR for contextualized ASR with controllable style* [Preprint available on arxiv](https://arxiv.org/abs/2309.07414)

**Note** The directory of audio files is hard-coded to `download/librilight` in the manifests.


## Leaderboard

**Note:** large subset=large + medium + small; medium subset = medium + small (i.e. large subset includes the large, medium, small manifests above, medium subset includes the medium and small manifests above).

### Models trained on normalized text

> Note: The models trained with Wenet might not be tuned well.

#### large subset

| contributor | toolkit | LibriSpeech WER (clean & other) | Libriheavy WER (clean & other) | recipe | model |
|-------------|---------|---------------------------------|--------------------------------|--------|-------|
| baseline    | Wenet   | 2.02 & 5.22                     |  2.74 & 6.68                   | [CTC + Attention]()  | [model]()       |
| baseline    | icefall | 1.62 & 3.36                     |  2.20 & 5.57                   | [Transducer]()       | [model]()      |


#### medium subset

| contributor | toolkit | LibriSpeech WER (clean & other) | Libriheavy WER (clean & other) | recipe | model |
|-------------|---------|---------------------------------|--------------------------------|--------|-------|
| baseline    | Wenet   | 3.15 & 7.88                     |  3.80 & 8.80                   | [CTC + Attention]()       | [model]()      |
| baseline    | icefall | 2.35 & 4.82                     |  2.90 & 6.57                   | [Transducer]()       | [model]()      |


#### small subset

| contributor | toolkit | LibriSpeech WER (clean & other) | Libriheavy WER (clean & other) | recipe | model |
|-------------|---------|---------------------------------|--------------------------------|--------|-------|
| baseline    | Wenet   | 5.76 & 15.60                    |  6.94 & 15.17                  | [CTC + Attention]()       | [model]()      |
| baseline    | icefall | 4.05 & 9.89                     |  4.68 & 10.01                  | [Transducer]()       | [model]()      |


### Models trained on text with casing and punctuation

#### large subset

| contributor | toolkit | Libriheavy normalized WER (clean & other) | Libriheavy WER (clean & other) | recipe | model |
|-------------|---------|-------------------------------------------|--------------------------------|--------|-------|
| baseline    | icefall |  2.28 & 5.68                              |  7.76 & 11.32                  | [Transducer]()       | [model]()       |

#### medium subset

| contributor | toolkit | Libriheavy normalized WER (clean & other) | Libriheavy WER (clean & other) | recipe | model |
|-------------|---------|-------------------------------------------|--------------------------------|--------|-------|
| baseline    | icefall |  3.05 & 6.78                              |  9.84 & 13.39                  | [Transducer]()       | [model]()      |

#### small subset

| contributor | toolkit | Libriheavy normalized WER (clean & other) | Libriheavy WER (clean & other) | recipe | model |
|-------------|---------|-------------------------------------------|--------------------------------|--------|-------|
| baseline    | icefall |  5.16 & 11.12                             | 13.04 & 19.54                  | [Transducer]()       | [model]()      |


## Citation

```
@misc{kang2023libriheavy,
      title={Libriheavy: a 50,000 hours ASR corpus with punctuation casing and context}, 
      author={Wei Kang and Xiaoyu Yang and Zengwei Yao and Fangjun Kuang and Yifan Yang and Liyong Guo and Long Lin and Daniel Povey},
      year={2023},
      eprint={2309.08105},
      archivePrefix={arXiv},
      primaryClass={eess.AS}
}
```
