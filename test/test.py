# SPDX-FileCopyrightText: 2026 Fayol Ateufack
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


def lfsr_step(state):
    """Reference model: 8-bit Fibonacci LFSR, polynomial x^8 + x^6 + x^5 + x^4 + 1."""
    fb = ((state >> 7) ^ (state >> 5) ^ (state >> 4) ^ (state >> 3)) & 1
    return ((state << 1) | fb) & 0xFF


async def reset_with_seed(dut, seed):
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = seed
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1


@cocotb.test()
async def test_lfsr_sequence(dut):
    """LFSR matches a software reference for one full period (255 cycles)."""
    dut._log.info("Start: LFSR sequence test")
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    seed = 0xAC
    await reset_with_seed(dut, seed)

    assert int(dut.uo_out.value) == seed, (
        f"After reset: got {int(dut.uo_out.value):#04x}, expected seed {seed:#04x}"
    )

    expected = seed
    states_seen = set()
    for i in range(255):
        states_seen.add(expected)
        expected = lfsr_step(expected)
        await ClockCycles(dut.clk, 1)
        actual = int(dut.uo_out.value)
        assert actual == expected, (
            f"Cycle {i + 1}: got {actual:#04x}, expected {expected:#04x}"
        )

    assert len(states_seen) == 255, (
        f"Sequence is shorter than 255 (only {len(states_seen)} unique states)"
    )
    assert expected == seed, (
        f"After full period: expected {seed:#04x}, got {expected:#04x}"
    )


@cocotb.test()
async def test_zero_seed_avoids_lockup(dut):
    """A seed of zero is replaced with 0x01 so the LFSR cannot lock at zero."""
    dut._log.info("Start: zero-seed lockup test")
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    await reset_with_seed(dut, 0)

    assert int(dut.uo_out.value) == 0x01, (
        f"With zero seed: expected 0x01 substitution, "
        f"got {int(dut.uo_out.value):#04x}"
    )

    seen = {0x01}
    for _ in range(20):
        await ClockCycles(dut.clk, 1)
        seen.add(int(dut.uo_out.value))
    assert len(seen) > 1, "LFSR appears stuck"
    assert 0 not in seen, "LFSR reached the all-zero state (should be impossible)"


@cocotb.test()
async def test_different_seeds_diverge(dut):
    """Different seeds produce different output streams (sanity check)."""
    dut._log.info("Start: seed independence test")
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    streams = {}
    for seed in (0x01, 0x42, 0xFF):
        await reset_with_seed(dut, seed)
        run = []
        for _ in range(16):
            await ClockCycles(dut.clk, 1)
            run.append(int(dut.uo_out.value))
        streams[seed] = run

    assert streams[0x01] != streams[0x42]
    assert streams[0x42] != streams[0xFF]
