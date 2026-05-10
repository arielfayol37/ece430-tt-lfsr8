/*
 * Copyright (c) 2026 Fayol Ateufack
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// 8-bit Fibonacci LFSR, polynomial x^8 + x^6 + x^5 + x^4 + 1.
// Produces a maximal-length pseudo-random sequence of period 255.
//
// ui_in   = seed (sampled while rst_n is low, before the chip starts running)
// uo_out  = current LFSR state (drive 8 LEDs)
// uio_*   = unused
module tt_um_arielfayol37 (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

  reg [7:0] state;

  // An all-zero seed would lock the LFSR at zero forever; substitute 0x01.
  wire [7:0] safe_seed = (ui_in == 8'h00) ? 8'h01 : ui_in;

  // Taps at positions 8, 6, 5, 4 (1-indexed) -> bits 7, 5, 4, 3 (0-indexed).
  wire feedback = state[7] ^ state[5] ^ state[4] ^ state[3];

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) state <= safe_seed;
    else        state <= {state[6:0], feedback};
  end

  assign uo_out  = state;
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  wire _unused = &{ena, uio_in, 1'b0};

endmodule
