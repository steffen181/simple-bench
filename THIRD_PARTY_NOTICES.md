# Third-party material

- BIG-Bench Hard, copyright 2022 suzgunmirac, MIT: [original license](https://github.com/suzgunmirac/BIG-Bench-Hard/blob/9ee07bd481feebf959a6b59d61ea57bdcf30964d/LICENSE), local `licenses/BIG-Bench-Hard-MIT.txt`. The packaged native contracts include demonstration text; the BBH generator/parser uses the tracking task's language templates. Original question datasets are obtained only with the explicit fetch command.
- Hugging Face fork of EleutherAI lm-evaluation-harness, MIT: [pinned repository](https://github.com/huggingface/lm-evaluation-harness/tree/c339225c8ec169296f45f5326a7c0f8e3baa6005), local `licenses/lm-evaluation-harness-MIT.txt`. Pinned task descriptions, demonstrations and configuration are retained in the native contract. The harness implementation itself is not vendored or installed by this package.
- Runtime dependencies PyYAML and Jinja2 are separately installed distributions with their own notices; they are not bundled into the source tree.

Source URLs and SHA256 hashes live in `src/tracking_bench/data/bbh-sources.json`. The project's own code is licensed under the [MIT License](LICENSE); see [license details](LICENSE_STATUS.md).

Please cite the upstream benchmark in research: Suzgun et al., *Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them*, [arXiv:2210.09261](https://arxiv.org/abs/2210.09261), and the BIG-bench collaboration, *Beyond the Imitation Game*, [arXiv:2206.04615](https://arxiv.org/abs/2206.04615).

- Optional campaign dependency python-igraph 0.11.9 is separately installed under its own GNU GPL terms. Its BLISS-backed graph canonicalization is used by the new v2 grouping; neither igraph nor model weights are vendored into this source distribution. See [igraph licensing](https://igraph.org/).
