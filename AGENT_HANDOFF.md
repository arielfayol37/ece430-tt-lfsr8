# Agent Handoff Guide — Tiny Tapeout Final Project

> **Audience:** another Claude (or any LLM coding agent) helping a student
> finish the **ECE429 (Integrated Circuits Fabrication)** final project at
> Valparaiso University, Spring 2026. The user you're working with is a
> classmate of **Fayol Ateufack**, who finished a similar project. This
> document is the cleaned-up playbook for that workflow.
>
> **What to do first:** read this file end-to-end before asking the user
> anything substantive. It compresses ~6 hours of prior trial-and-error into
> a sequence you can follow without re-discovering each pitfall.

---

## 1. Course context (in one screen)

- **Class:** ECE429, Spring 2026, Valparaiso University. Homework pages live
  at `https://agnd.net/valpo/429/hwNN.html` (replace `NN` with `05`–`09`)
  and `https://agnd.net/valpo/429/final.html`.
- **Flow:** [Tiny Tapeout](https://tinytapeout.com/) — students design a
  small digital circuit in Verilog, push to a GitHub repo derived from
  `TinyTapeout/ttsky-verilog-template`, and GitHub Actions runs the
  open-source LibreLane flow to produce a sky130 GDSII layout. The student
  may optionally submit it for fabrication (TTSKY26b shuttle); most don't.
- **Hardware constraints (do not violate these):**
  - One tile of `1 × 1` ≈ 167 µm × 108 µm. Keep gate count small.
  - Fixed pinout: `ui_in[7:0]` (in), `uo_out[7:0]` (out), `uio_in[7:0]`
    (bidir-in), `uio_out[7:0]`, `uio_oe[7:0]`, plus `clk`, `rst_n`, `ena`.
  - Top module name **must** start with `tt_um_` and **must** be unique
    across all TT projects. Convention: `tt_um_<github_username>` or
    `tt_um_<github_username>_<short_design_name>`.
  - Clock period in `src/config.json` defaults to 20 ns (50 MHz). Don't
    change unless necessary.
- **Deliverables (from `hw09` and `final.html`):**
  1. Working Verilog top module + cocotb tests, all green in CI.
  2. `info.yaml` filled out with author, top module name, pinout descriptions.
  3. `docs/info.md` with: how-it-works narrative, block diagram, pin table,
     waveform screenshots. (TT renders this into a PDF datasheet.)
  4. A short presentation (5–7 min) at the May 13 class meeting with: pin
     assignment table, block diagram, behavioural description, GDS layout
     screenshot.
  5. Final repo deadline May 15.

---

## 2. The reference design (read this for context)

Fayol's finished project lives at
[`github.com/arielfayol37/ece430-tt-lfsr8`](https://github.com/arielfayol37/ece430-tt-lfsr8)
(yes, the repo name says "ece430" — that's a typo, the course is 429).
It's an 8-bit Fibonacci LFSR; the **structure of the repo** is what you want
to imitate, not the design itself.

Key files and what they're for:

| Path | What it is | Why it's worth modelling |
|---|---|---|
| `src/project.v` | The Verilog top module. | One small file with clear inputs/outputs and a single `always` block. Keep the friend's design at this size. |
| `info.yaml` | TT project metadata: title, author, top-module name, pinout descriptions, clock frequency. | Required by the TT build. Pin descriptions become column 2 of the datasheet. |
| `test/test.py` | Three cocotb tests: sequence match, edge case, sanity check. | Good template for any sequential design. |
| `test/tb.v` | The Verilog testbench wrapper. **Only edit the module instance name** to match the new top module. | Don't over-engineer this. |
| `docs/info.md` | The user-facing datasheet. | Section headings: *How it works*, *How to test*, *Layout*, *Pin assignments*, *External hardware*. |
| `docs/block_diagram.png` | A real diagram (not ASCII art). | Required by hw09. |
| `docs/waveform.png` | Screenshot of the cocotb simulation. | Required by hw09. |
| `docs/gds_render.png` | The rendered GDSII layout. | Required by the presentation. |
| `docs/PRESENTATION.md` | A long-form study guide. | Helpful for the friend to actually understand their own design. |
| `docs/slides.html` | A self-contained reveal.js deck. | Speaker notes per slide. |
| `README.md` | Project-specific front page (not template boilerplate). | First impression for the prof. |

Look at any of those files in the reference repo if you need a concrete
shape to copy.

---

## 3. Picking the project

### 3.1 Criteria for "good for this assignment"

A project is a good fit if **all** of these are true:

- Fits in ~50–500 µm² of standard cells. Translated: under ~100 flops,
  under ~500 gates. If you can describe the design in 30 lines of Verilog,
  you're safe.
- Uses only the standard TT pinout. No external memory, no DACs, no PLLs.
- Has a clean input/output story the student can explain in one sentence.
  ("You give it X, it gives you Y.")
- Produces something you can demonstrate visually on slides — LEDs lighting
  up, a 7-seg display, a waveform with a recognisable pattern.
- Synthesisable to sky130 cells. Avoid: async reset to non-constant values
  (see Pitfall 1), latches, multi-driver nets, gated clocks.

Reject anything that requires off-chip memory, an analog block, a parser,
or "I want to implement RISC-V". Those are six-month projects.

### 3.2 Three vetted starter options

Offer the user these three, recommend the simplest, but follow their lead.

**Option A — 7-segment dice roller (combinational decode + counter)**
- Inputs: `ui_in[0]` = button. While held, a fast counter cycles 1–6;
  release → display freezes.
- Outputs: `uo_out[6:0]` drives a 7-seg digit; `uo_out[7]` is the LED
  indicating the button state.
- Internals: 3-bit counter (mod 6) + 7-bit segment lookup table.
- ~10 flops + small combinational lookup. Easy to visualise on slides.
- Talking point: "fast counter + sample on release = statistically fair
  randomness without a true RNG."

**Option B — 8-bit LFSR (the reference design)**
- Inputs: `ui_in[7:0]` = seed.
- Outputs: `uo_out[7:0]` = current state.
- Internals: 8 flops, one XOR, 8 muxes for seed load.
- See the reference repo. Strongest "real engineering" talk.
- Talking point: "LFSRs are everywhere — Ethernet CRC, PCIe scramblers,
  BIST in CPUs."

**Option C — PWM LED dimmer (datapath + comparator)**
- Inputs: `ui_in[7:0]` = duty cycle (0–255).
- Outputs: `uo_out[7:0]` = PWM signal, all 8 bits mirrored so a single LED
  bar visibly dims.
- Internals: 8-bit free-running counter + 8-bit comparator. Maybe 16 flops.
- Smallest of the three.
- Talking point: "how a 1-bit digital output approximates analog."

**Other ideas if those don't appeal**, in roughly increasing difficulty:
Knight Rider LED chaser, traffic light FSM, stopwatch (clock divider +
counter + 7-seg), reaction-timer game, binary-to-BCD converter, frequency
divider, tone generator, simple 4-bit ALU, UART transmitter. Anything with
a state-machine flavour works well and gives a story to tell.

### 3.3 What to ask the user before starting

1. **GitHub username** — for the top-module name.
2. **Project preference** — give them the three options, recommend one,
   accept their choice.
3. **Project title for `info.yaml`** — a one-line human-readable name.
4. **Whether they've already created the GitHub repo** — and if so, the
   URL. (Most likely "no, but the prof showed me the TT template.")
5. **Their name** as it should appear in `info.yaml` and the README.

You probably don't need to ask: clock frequency (keep the 50 MHz default),
discord, or anything else in `info.yaml` beyond title/author/top_module.

---

## 4. The implementation playbook

Execute these in order. Don't skip.

### Step 0 — Repo creation (let the user do this themselves)

Tell the user to **create the repo via the GitHub template button**, not by
forking or cloning. The template button creates a fresh repo with a single
initial commit, GitHub Actions enabled, and the right repo settings.

```
https://github.com/TinyTapeout/ttsky-verilog-template
→ "Use this template" → "Create a new repository"
→ name it something like tt-<short_name>
→ public (required so TT's docs deploy can publish to Pages)
→ Create.
```

Then tell the user to **enable GitHub Pages immediately**, before pushing:

```
Settings → Pages → Source: GitHub Actions → Save.
```

If they skip this, the `gds/viewer` job will fail on every push with a 404.
We learned this the hard way.

### Step 1 — Get a working local copy

There are two clean ways:

**Recommended:** clone the user's fresh new repo:
```
git clone https://github.com/<user>/<repo>.git
cd <repo>
```

**Acceptable alternative** (we used this on Fayol's project): take an
existing clone of the TT template, re-point its `origin`, then force-push:
```
git remote set-url origin https://github.com/<user>/<repo>.git
git push --force origin main
```
This works but feels wrong — only do it if the user already has a clone of
the TT template and would rather not re-clone.

### Step 2 — Scaffold the five files

You'll edit exactly these files:

1. **`src/project.v`** — rename `tt_um_example` → `tt_um_<github_username>`
   and replace the body with the new design. Keep the port list shape.
2. **`info.yaml`** — fill in title, author, top_module, source_files,
   clock_hz (50000000), tiles (1x1), and the pinout descriptions (column
   2 of the slide pin table).
3. **`test/tb.v`** — change exactly one line, the `tt_um_example
   user_project (...)` instance name to `tt_um_<github_username>
   user_project (...)`. Don't touch the rest.
4. **`test/test.py`** — replace the trivial example test with real tests
   for the new design. See Section 5 for the cocotb pattern that actually
   works.
5. **`docs/info.md`** — replace the placeholder content with: "How it
   works" narrative, block diagram reference, "How to test" steps, pin
   assignments table, "External hardware" (usually "None").

**Do not** edit `src/config.json` (LibreLane defaults), `test/Makefile`
(unless adding more `.v` source files via `PROJECT_SOURCES`), `.devcontainer/`,
or `.github/workflows/`. They're tuned and work as-is.

### Step 3 — First push

Commit and push. Watch the Actions tab. Expect:
- `test` to pass (~30s) if the cocotb test is right.
- `gds` to pass (~3 min) if the Verilog synthesises cleanly.
- `gds/viewer` to publish to Pages (~30s) if you enabled Pages in step 0.
- `docs` to build the datasheet PDF (~1 min).
- `fpga` may or may not pass — non-blocking, can be ignored.

### Step 4 — Build the assets

Once `test` and `gds` are green, the friend needs three images:

1. **Block diagram** (`docs/block_diagram.png`).
   - Hand-coding an SVG works but looks amateurish. Better:
     give the user a polished prompt (see section 6) and have them paste
     it into ChatGPT / Excalidraw AI / draw.io to generate a PNG. Then
     commit the PNG.
   - **Avoid spaces in filenames** (see Pitfall 4).

2. **Waveform** (`docs/waveform.png`).
   - GitHub Actions uploads `tb.fst` as an artifact of the `test` workflow.
     Download → drag into <https://app.surfer-project.org/> → add signals
     `tb.user_project.clk`, `rst_n`, `ui_in[7:0]`, `state[7:0]`,
     `uo_out[7:0]` (and any design-specific internal signals) → right-click
     buses → Display format → Hex → screenshot.
   - No install required.

3. **GDS render** (`docs/gds_render.png`).
   - The `gds` workflow uploads an artifact called `gds_render` (~120 KB)
     that contains a pre-rendered PNG. Just download and commit it.
   - Do **not** try to install KLayout for the screenshot — the
     `gds_render` artifact already exists.

### Step 5 — Reference assets in `docs/info.md`

```markdown
![Block diagram](block_diagram.png)
![Simulation waveform](waveform.png)
![GDS layout](gds_render.png)
```

Plain relative paths. No `<…>` angle-bracket form, no `%20` escapes — see
Pitfall 4.

### Step 6 — Build the presentation

The reference repo's `docs/slides.html` is a self-contained reveal.js deck
loaded from CDN. Copy it as a starting template, swap in the friend's
content, keep the speaker-notes-per-slide pattern. Outline:

1. Title
2. What is Tiny Tapeout (one slide of context for non-TT audience)
3. The design (one paragraph + key parameters)
4. Why it matters (real-world uses of this class of circuit)
5. Architecture (block diagram)
6. The Verilog (paste the core ~5 lines)
7. Pin assignments (table)
8. Verification (mention each test + a green pass banner)
9. Waveform
10. From RTL to silicon (GDS render + flow stages)
11. What I learned (3–4 specific gotchas — synthesis lessons, sim lessons)
12. Q&A / Thanks

### Step 7 — Rewrite the README

The TT template `README.md` is generic boilerplate. Replace it with a
project-specific front page: title, one-line pitch, live Pages URL, file
navigation table, how-to-test-locally snippet, author/course block. The
reference repo's `README.md` is a good shape to copy.

---

## 5. Specific failures we hit (and the fix for each)

### Pitfall 1 — Async reset to a non-constant value

**Symptom:** `gds` workflow fails with
`ERROR Unmapped Yosys instances found. <N>` where N equals the number of
flops in the design.

**Root cause:** sky130 standard-cell flip-flops have async reset to a
constant (0 or 1) but cannot async-load an arbitrary value. Code like
this:
```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) state <= safe_seed;   // <-- safe_seed is a wire, not a constant
    else        state <= ...;
end
```
gives Yosys no library cell to map to.

**Fix:** switch to **synchronous reset**:
```verilog
always @(posedge clk) begin
    if (!rst_n) state <= safe_seed;
    else        state <= ...;
end
```
This becomes a 2:1 mux on the D input of each flop, which maps cleanly.
TT holds `rst_n` low for many cycles after power-up, so the seed gets
loaded reliably.

If you genuinely need async reset, it must be to a **constant only**:
```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) state <= 8'h00;        // OK — constant
    else if (...) state <= safe_seed;  // sync load
    else state <= ...;
end
```

### Pitfall 2 — cocotb 2.0 sequential-logic sampling

**Symptom:** sequence tests fail at cycle 1 with the *seed* value instead
of the expected first state. The earlier cycles look stale by one.

**Root cause:** in cocotb 2.x, `await RisingEdge(dut.clk)` returns *at*
the active edge, before non-blocking assignments inside `always @(posedge
clk)` have propagated. Reading `dut.signal.value` right after returns
the pre-edge value.

**Fix:** sample on the falling edge instead. Pattern:
```python
from cocotb.triggers import FallingEdge

# Wait one full clock cycle, sample with NBAs settled:
await FallingEdge(dut.clk)
actual = int(dut.signal.value)
```
And during reset, deassert `rst_n` at a falling edge for predictable
timing:
```python
async def reset_with_seed(dut, seed):
    dut.ui_in.value = seed
    dut.rst_n.value = 0
    for _ in range(5):
        await FallingEdge(dut.clk)
    dut.rst_n.value = 1
```

### Pitfall 3 — GitHub Pages not enabled

**Symptom:** `gds/viewer` job fails with
`Error: Creating Pages deployment failed: HttpError: Not Found` and the
suggestion link to enable Pages.

**Fix:** Repo Settings → Pages → Source: **GitHub Actions** (not "Deploy
from a branch") → Save. Re-run the failed job. This only needs to be done
once. **Tell the user to do this immediately after creating the repo, not
after the first failed CI run.**

### Pitfall 4 — Image filenames with spaces

**Symptom:** `docs` workflow fails with
`error: file not found (searched at …/FST%20Waveform.png)` from typst.

**Root cause:** the TT docs pipeline is pandoc → typst. Pandoc
URL-encodes spaces in image paths (`Foo Bar.png` → `Foo%20Bar.png`),
typst then can't find the literal filename.

**Fix:** never include spaces in filenames under `docs/`. If the user
uploads `FST Waveform.png`, rename it to `waveform.png` before referencing
it. Also avoid the `![alt](<path with spaces>)` markdown form for the
same reason.

### Pitfall 5 — Origin pointed at the TT template

**Symptom:** running `git remote -v` shows
`origin https://github.com/TinyTapeout/ttsky-verilog-template`. Pushes
fail with permission denied, or worse, succeed against a fork the user
didn't intend.

**Fix:** before any push, run:
```sh
git remote set-url origin https://github.com/<user>/<repo>.git
git remote -v   # verify it now points at the user's repo
```

### Pitfall 6 — Wrong top-module name typo

The user may type their GitHub username slightly wrong (`arilefayol37` vs
`arielfayol37`). The top-module name will be baked into the silicon
metadata. Confirm the spelling against their actual GitHub URL before
committing.

### Pitfall 7 — `.DS_Store` in commits

macOS Finder drops `.DS_Store` files in any folder a user opens. The
template `.gitignore` already excludes them, but if a user `git add .`s
they'll slip in. Add specific files by name (`git add docs/foo.png`)
rather than `git add .` or `git add -A`.

---

## 6. Tooling shortcuts

### Waveform viewing
- **Surfer** (browser): <https://app.surfer-project.org/> — drop `tb.fst`
  in, no install, works on Chromebook.
- **GTKWave** (desktop): `brew install gtkwave` on macOS. Same `.fst`
  file. Preferred if the user wants to fiddle.

### GDS viewing
- The `gds` workflow's `gds_render` artifact already contains a PNG.
  Use that. Do not install KLayout just for the screenshot.
- If the user wants to interact with the layout: `brew install --cask
  klayout` on macOS, then `open <design>.gds`.

### Block diagram generation
- Hand-coded SVG works but looks amateurish. For polished output, give
  the user this prompt:

  > Create a clean, professional digital-logic block diagram of <design>
  > for a college presentation slide. Style: minimalist engineering
  > schematic, white background, thin dark-gray lines, sans-serif labels,
  > like a textbook figure.
  >
  > Layout left-to-right: <inputs> on the left, <central architecture
  > description> in the middle, <outputs> on the right. <Specific
  > callouts: tap connections, feedback paths, clock broadcast, etc.>
  >
  > Title at top: "<design name> — tt_um_<username>"
  > Subtitle: "<one-line summary>"

  Then have them paste it into ChatGPT with image generation,
  Excalidraw AI, or draw.io's AI assistant.

### Slides
- Reveal.js from CDN works without install. Open `slides.html` in a
  browser, press `S` for the speaker-notes window, press `F` for
  fullscreen.
- For PDF backup (no internet in the room): open
  `slides.html?print-pdf` in Chrome → File → Print → Save as PDF.

### Local simulation
- `cd test && make` — if `iverilog` and `cocotb` are installed.
- On macOS without them: `brew install icarus-verilog`, `pip install
  cocotb cocotb-bus`.
- **If they're not installed, don't bother trying to install them.**
  GitHub Actions will run the tests on push. The cycle time is 30s — 
  faster than installing tools.

---

## 7. Suggested conversation opener

Once you've read this file, lead the conversation like this:

> "I'm helping you with your ECE429 final project. I've read a guide your
> classmate Fayol put together from his finished project, so I have a
> good idea of the flow. Quick questions to get started:
>
> 1. Do you have a project idea in mind, or would you like me to suggest a
>    few simple ones you can finish in a few hours?
> 2. What's your GitHub username? I'll need it for the top-module name.
> 3. Have you already created the GitHub repo from the TT template, or
>    should we do that now?
>
> Once we have those, I'll scaffold the code and walk you through
> enabling GitHub Pages (one click, but it's the one thing that's easy
> to forget). After that, we push, and GitHub Actions does most of the
> heavy lifting."

Don't recite the whole playbook to the user — they don't need it. Use
it as your own reference and surface only the parts they need to act
on.

---

## 8. Honest assessment of the workflow

Things that genuinely worked well:
- The TT "Use this template" button → clean repo with Actions ready.
- Surfer in the browser for waveforms. Zero install.
- The `gds_render` artifact for layout screenshots. Zero install.
- Reveal.js from CDN for slides. Zero install.
- The 3-test cocotb pattern: (a) full reference-model match for a long
  trace, (b) edge case, (c) sanity check. Catches almost everything.

Things that could be smoother for the next project:
- The first GDS run almost always fails on something — async-reset
  mapping, an unmapped cell, a lint error. Build in a 15-minute buffer
  for one iteration cycle.
- The block-diagram step is the most time-consuming part if done well.
  Decide early whether the user wants "good enough" (an SVG you write)
  or "polished" (have an image generator make it). The middle ground
  wastes time.
- Don't over-engineer the testbench. Three tests is enough. Four is
  fine. Ten is procrastination.

End of guide. Now: go talk to the user.
