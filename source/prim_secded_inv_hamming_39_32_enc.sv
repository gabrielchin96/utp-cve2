// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// SECDED encoder generated by util/design/secded_gen.py

module prim_secded_inv_hamming_39_32_enc (
  input        [31:0] data_i,
  output logic [38:0] data_o
);

  always_comb begin : p_encode
    data_o = 39'(data_i);
    data_o[32] = 1'b0 ^ ^(data_o & 39'h0056AAAD5B);
    data_o[33] = 1'b1 ^ ^(data_o & 39'h009B33366D);
    data_o[34] = 1'b0 ^ ^(data_o & 39'h00E3C3C78E);
    data_o[35] = 1'b1 ^ ^(data_o & 39'h0003FC07F0);
    data_o[36] = 1'b0 ^ ^(data_o & 39'h0003FFF800);
    data_o[37] = 1'b1 ^ ^(data_o & 39'h00FC000000);
    data_o[38] = 1'b0 ^ ^(data_o & 39'h3FFFFFFFFF);
  end

endmodule : prim_secded_inv_hamming_39_32_enc
