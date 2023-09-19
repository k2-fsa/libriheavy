# Creation pipeline

This is the documentation of creating Libriheavy asr corpus (i.e. splitting the training, dev and test sets). If you want
to know how we align Librilight to be Libriheavy, please see [text search libriheavy recipe](https://github.com/k2-fsa/text_search/tree/master/examples/libriheavy) for details.

**Note:** We can not guarantee that the pipeline will produce the same manifests as ours, because we select test and dev sets randomly from a "pool", read our [paper](https://arxiv.org/pdf/2309.08105.pdf) for more details.


## Download raw manifests aligned by [text search](https://github.com/k2-fsa/text_search/tree/master/examples/libriheavy)

from huggingface:

```
bash run_pipeline.sh --stage 1 --stop-stage 1
```

or from modelscope

```
bash run_pipeline.sh --stage 0 --stop-stage 0
```

## Filter out the segments with higher CER (Optional)

We allow some errors when aligning the audios to avoid dropping out too much data, you can filter out those segments with higher CER if you like.

```
bash run_pipeline.sh --stage 2 --stop-stage 2
```

You can specify the `threshold`, see `scripts/filter_by_cer.py` for details.

## Get speakers and books for dev and test sets and excluding them from training sets

```
bash run_pipeline.sh --stage 3 --stop-stage 3
```

## Split dev and test sets

```
bash run_pipeline.sh --stage 4 --stop-stage 4
```

Congratulations, you have gotten the Libriheavy corpus, see [README](./README.md) for how to use it.
