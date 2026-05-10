# SPDX-FileCopyrightText: 2026 Fayol Ateufack
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge


def lfsr_step(state):
    """Reference model: 8-bit Fibonacci LFSR, polynomial x^8 + x^6 + x^5 + x^4 + 1."""
    fb = ((state >> 7) ^ (state >> 5) ^ (state >> 4) ^ (state >> 3)) & 1
    return ((state << 1) | fb) & 0xFF


async def reset_with_seed(dut, seed):
    """Hold reset for several cycles with the seed on ui_in.

    Reset is deasserted at a falling edge, leaving the design ready for the
    next rising edge to start shifting. After this returns, the testbench is
    aligned to a falling edge so reads are after the previous edge's NBAs
    have settled.
    """
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = seed
    dut.rst_n.value = 0
    for _ in range(5):
        await FallingEdge(dut.clk)
    dut.rst_n.value = 1


@cocotb.test()
async def test_lfsr_sequence(dut):
    """LFSR matches a software reference for one full period (255 cycles)."""
    dut._log.info("Start: LFSR sequence test")
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    seed = 0xAC
    await reset_with_seed(dut, seed)

    actual = int(dut.uo_out.value)
    assert actual == seed, (
        f"After reset: got {actual:#04x}, expected seed {seed:#04x}"
    )

    expected = seed
    states_seen = {expected}
    for i in range(255):
        expected = lfsr_step(expected)
        await FallingEdge(dut.clk)
        actual = int(dut.uo_out.value)
        assert actual == expected, (
            f"Cycle {i + 1}: got {actual:#04x}, expected {expected:#04x}"
        )
        states_seen.add(actual)

    assert len(states_seen) == 255, (
        f"Sequence has only {len(states_seen)} unique states (expected 255)"
    )
    assert expected == seed, (
        f"Did not return to seed after full period: got {expected:#04x}"
    )


@cocotb.test()
async def test_zero_seed_avoids_lockup(dut):
    """A seed of zero is replaced with 0x01 so the LFSR cannot lock at zero."""
    dut._log.info("Start: zero-seed lockup test")
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    await reset_with_seed(dut, 0)

    assert int(dut.uo_out.value) == 0x01, (
        f"Zero seed: expected 0x01 substitution, got {int(dut.uo_out.value):#04x}"
    )

    seen = {0x01}
    for _ in range(20):
        await FallingEdge(dut.clk)
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
            await FallingEdge(dut.clk)
            run.append(int(dut.uo_out.value))
        streams[seed] = run

    assert streams[0x01] != streams[0x42]
    assert streams[0x42] != streams[0xFF]
