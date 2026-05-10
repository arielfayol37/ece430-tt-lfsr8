![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# 8-bit LFSR Pseudo-Random Generator (`tt_um_arielfayol37`)

A maximal-length 8-bit Fibonacci Linear Feedback Shift Register, hardened to a
sky130 GDSII layout via the open-source [Tiny Tapeout](https://tinytapeout.com)
flow. Polynomial **x⁸ + x⁶ + x⁵ + x⁴ + 1**, period 255, ~50 µm² of real logic.

**Live datasheet:** <https://arielfayol37.github.io/ece430-tt-lfsr8/>

## What's here

| Path | Purpose |
|---|---|
| [`src/project.v`](src/project.v) | Verilog top module — 8 flops, one XOR, synchronous seed-load. |
| [`test/test.py`](test/test.py) | Three cocotb tests: full-period sequence match, zero-seed safety, seed independence. |
| [`info.yaml`](info.yaml) | Tiny Tapeout project metadata + pin assignments. |
| [`docs/info.md`](docs/info.md) | The public datasheet rendered by the TT docs pipeline. |
| [`docs/PRESENTATION.md`](docs/PRESENTATION.md) | Detailed study guide — LFSR theory, line-by-line walkthroughs of the Verilog and tests, slide-ready pin table, sample sequence, anticipated Q&A. |
| [`docs/slides.html`](docs/slides.html) | Reveal.js slide deck for the final-project presentation. |
| [`docs/block_diagram.png`](docs/block_diagram.png) | Architecture diagram (8 flops + XOR feedback + taps). |
| [`docs/waveform.png`](docs/waveform.png) | Cocotb simulation trace, viewed in Surfer. |
| [`docs/gds_render.png`](docs/gds_render.png) | Final hardened GDSII layout from LibreLane. |

## How it works (in one paragraph)

While `rst_n` is held low, the chip loads `ui_in[7:0]` into its 8-bit state
register. When reset is released, every rising clock edge shifts the register
left by one bit; the bit shifted in at the LSB is the XOR of taps at bit
positions 8, 6, 5, 4. After exactly 255 cycles the register returns to the
seed and the sequence repeats. The current state is exposed on `uo_out[7:0]`,
which can drive an 8-LED bar to visualise the pseudo-random pattern.

## How to test locally

```sh
cd test
make            # RTL simulation with Icarus Verilog + cocotb
```

The simulation produces `tb.fst` — open it in [Surfer](https://surfer-project.org)
(browser-based) or GTKWave to inspect waveforms.

For the full chip-hardening pipeline (Yosys → LibreLane → sky130 GDSII),
just push to the repo: GitHub Actions runs `gds`, `test`, `fpga`, and `docs`
workflows automatically.

## Author

**Fayol Ateufack** — ECE429 (Integrated Circuits Fabrication), Spring 2026,
Valparaiso University. Final project.

## What is Tiny Tapeout?

[Tiny Tapeout](https://tinytapeout.com) is an educational program that pools
many small student designs onto a single shared die in the SkyWater 130 nm
process, making real chip fabrication accessible at a few-tens-of-dollars cost
per design. Each project gets a 1×1 tile (~167 µm × 108 µm) and a fixed pinout
of 8 inputs, 8 outputs, 8 bidirectionals, plus clock, reset, and enable.

## Resources

- [Tiny Tapeout FAQ](https://tinytapeout.com/faq/)
- [Local hardening guide](https://tinytapeout.com/guides/local-hardening/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Surfer waveform viewer](https://app.surfer-project.org/)
