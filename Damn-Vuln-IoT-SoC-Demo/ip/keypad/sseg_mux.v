`timescale 1ns / 1ps

module sseg_mux(
    input clk, rst,
    input [6:0] dig0, dig1, dig2, dig3,
    output reg [3:0] an,
    output reg [6:0] sseg
    );
    
    // refresh rate of ~1526Hz (100 MHz / 2^16)
    localparam BITS = 18;

    counter_n #(.BITS(BITS)) counter(.clk(clk), .rst(rst), .q(q));
    
    wire [BITS - 1 : 0] q;
            
    always @*
        case (q[BITS - 1 : BITS - 2])
            2'b00:
                begin
                    an = 4'b1110;
                    sseg = dig0;
                end
            2'b01:
                begin
                    an = 4'b1101;
                    sseg = dig1;
                end
            2'b10:
                begin
                    an = 4'b1011;
                    sseg = dig2;
                end
            default:
                begin
                    an = 4'b0111;
                    sseg = dig3;
                end
        endcase

endmodule
