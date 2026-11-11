# Third-party source notices and provenance

This directory preserves upstream notices for source included in the private CSAW evidence repository. It does not relicense the course assignment, student records, or all repository contents under one blanket license.

## Supplied clean AES reference

The three AES design sources `aes_128.v`, `round.v`, and `table.v`, plus the ordinary testbench `tb_aes_128.v`, retain their original copyright 2012 Homer Hsing and Apache License 2.0 headers. They were supplied in the professor's course package and are unchanged. Their use is ordinary reference verification, separate from the recovered CSAW design. No published challenge solution was obtained for this license check.

`Apache-2.0.txt` is the complete license text obtained from [the Apache Software Foundation](https://www.apache.org/licenses/LICENSE-2.0.txt). Keep it with the unchanged source headers. No additional AES-specific NOTICE file was present in the supplied source subset. Exact files and matching supplied-package hashes are recorded in `LICENSE_PROVENANCE.json`.

## Yosys iCE40 simulation cells

`core_evidence/verification/baseline_equivalence/simulation/sources/cells_sim.v` is unchanged from the local OSS CAD Suite 20261106 installation used in the preserved experiment. The exact file hash is `b5b2bcd86c0d6eea269015aaebff1d5fb66e7ec3f7eded0bde07406e5ac99527`. The local suite's bundled Yosys license names revision `2f2307ad6041d423c2fcaa7915ac295d09f14e53`; the experiment records Yosys 0.70+344 (2f2307ad6).

`YOSYS-ISC.txt` preserves the corresponding ISC license section and Claire Xenia Wolf copyright notice. `YOSYS-BUNDLED-LICENSE.txt` preserves the full bundled license/provenance file unchanged, including its upstream/dependency acknowledgements. Only the simulation-source file is included; the extra notices do not imply that the suite's binaries or every dependency is redistributed.

## HW2VEC

`HW2VEC-MIT.txt` is copied unchanged from the professor package's `hw2vec/LICENSE` and retains the 2021 louisccc copyright notice. It accompanies the retained detector-method provenance. This compact repository does not include a complete HW2VEC installation, checkpoints, or dataset RTL. This notice does not establish licensing of separately supplied checkpoint/data assets or arbitrary other notebook code.

## Other materials

The recovered baseline, challenge-provided host/interface material, experiment output, correspondence and bounded agent records retain their own documented origins. These supplemental notices do not assert that the student owns or may publicly relicense all of those materials. Keep the repository private and avoid a blanket repository license that would misdescribe those sources.

The checks here preserve actual upstream notices and provenance. No build, simulation, detector inference, generation workflow or payload was executed to prepare this directory. No historical source or evidence package was modified.
