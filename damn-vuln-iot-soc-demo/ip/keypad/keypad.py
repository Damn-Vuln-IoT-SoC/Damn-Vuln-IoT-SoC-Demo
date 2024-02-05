import os
from migen import *
from migen.genlib.misc import WaitTimer

from litex.soc.interconnect.csr import *
from litex.soc.interconnect import wishbone
from litex.soc.cores.gpio import GPIOIn

from litex.soc.integration.config import Config

class Keypad(Module, AutoCSR):
    def __init__(self, platform):

        config_parser = Config.getInstance()
        self.current_key = config_parser.getString("admin_dashboard_key")
        
        # Retrieve Signals from GPIO
        self.col_4 = platform.request("col4")
        self.col_3 = platform.request("col3")
        self.col_2 = platform.request("col2")
        self.col_1 = platform.request("col1")

        self.row_4 = platform.request("row4")
        self.row_3 = platform.request("row3")
        self.row_2 = platform.request("row2")
        self.row_1 = platform.request("row1")

        self.counter = Signal(3)
        self.state = Signal(4, reset=0)
        self.value = Signal(16)
        self.status = CSRStatus(1)

        self.key = Signal(4)

        platform.add_source_dir(path=os.path.dirname(__file__))

        self.cols = Cat(self.col_4, self.col_3, self.col_2, self.col_1)
        self.rows = Cat(self.row_4, self.row_3, self.row_2, self.row_1)

        self.keypad_params = dict(
            i_clk = ClockSignal("sys"),
            i_reset = ResetSignal("sys"),
            i_row = self.rows,
            io_col = self.cols,
            o_key = self.key
        )

        self.sync += [
            self.state.eq(self.key),
            If(self.key != self.state,
                If(self.counter == 0,
                    self.value.eq(0),
                    self.value[12:16].eq(self.key),
                    self.counter.eq(1)),
                If(self.counter == 1,
                    self.value[8:12].eq(self.key),
                    self.counter.eq(2)),
                If(self.counter == 2,
                    self.value[4:8].eq(self.key),
                    self.counter.eq(3)),
                If(self.counter == 3,
                    self.value[0:4].eq(self.key),
                    self.counter.eq(4)),
            ),
            If(self.counter == 4,
                self.status.status.eq(1),
                If(self.value[12:16] != int(self.current_key[0], 16),
                    self.status.status.eq(0),
                    self.value.eq(0)
                ),
                If(self.value[8:12] != int(self.current_key[1], 16),
                    self.status.status.eq(0),
                    self.value.eq(0)
                ),
                If(self.value[4:8] != int(self.current_key[2], 16),
                    self.status.status.eq(0),
                    self.value.eq(0)
                ),
                If(self.value[0:4] != int(self.current_key[3], 16),
                    self.status.status.eq(0),
                    self.value.eq(0)
                ),
                self.counter.eq(0)
            )
        ]

        self.specials += Instance("pmod_keypad", **self.keypad_params)


        # Display key on 7SEG

        self.segs = Cat(platform.request("seg0"), platform.request("seg1"), platform.request("seg2"), platform.request("seg3"), platform.request("seg4"), platform.request("seg5"), platform.request("seg6"))
        self.ans = Cat(platform.request("an0"), platform.request("an1"), platform.request("an2"), platform.request("an3"))

        self.seg0 = Signal(7)
        self.seg1 = Signal(7)
        self.seg2 = Signal(7)
        self.seg3 = Signal(7)

        self.ss7_0 = dict(
            i_hex = self.value[0:4],
            o_seg = self.seg0
        )

        self.ss7_1 = dict(
            i_hex = self.value[4:8],
            o_seg = self.seg1
        )

        self.ss7_2 = dict(
            i_hex = self.value[8:12],
            o_seg = self.seg2
        )

        self.ss7_3 = dict(
            i_hex = self.value[12:16],
            o_seg = self.seg3
        )

        self.specials += Instance("sseg_display", **self.ss7_0)
        self.specials += Instance("sseg_display", **self.ss7_1)
        self.specials += Instance("sseg_display", **self.ss7_2)
        self.specials += Instance("sseg_display", **self.ss7_3)

        self.ss7_mux = dict(
            i_clk = ClockSignal("sys"),
            i_rst = ResetSignal("sys"),
            i_dig0 = self.seg0,
            i_dig1 = self.seg1,
            i_dig2 = self.seg2,
            i_dig3 = self.seg3,
            o_an = self.ans,
            o_sseg = self.segs
        )

        self.specials += Instance("sseg_mux", **self.ss7_mux)