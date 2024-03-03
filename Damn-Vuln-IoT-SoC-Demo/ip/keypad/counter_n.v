`timescale 1ns / 1ps

module counter_n
    # (BITS = 4)
    (
    input clk,
    input rst,
    output tick,
    output [BITS - 1 : 0] q
    );
    
    // counter register
    reg [BITS - 1 : 0] rCounter = 0;
    
    // increment or reset the counter
    always @ (posedge clk, posedge rst)
        if (rst)
            rCounter <= 0;
        else
            rCounter <= rCounter + 1;

    // connect counter register to the output wires
    assign q = rCounter;
    
    // set the tick output
    assign tick = (rCounter == 2 ** BITS - 1) ? 1'b1 : 1'b0;
        
endmodule
