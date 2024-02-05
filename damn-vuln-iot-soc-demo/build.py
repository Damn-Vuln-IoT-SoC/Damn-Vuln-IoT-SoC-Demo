#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020-2021 Xuanyu Hu <xuanyu.hu@whu.edu.cn>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.led import *
from litex.soc.integration.config import Config

from config import board
from ip.jtag_lock import *
from ip.random import Counter
from ip.keypad import Keypad
from ip.lock import AddLockHandler

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):

        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_vga       = ClockDomain()

        self.submodules.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(platform.request("user_btnc") | self.rst)

        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_vga, 40e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.
        platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets jtag_tck_IBUF]")

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    config_parser = Config.getInstance()
    if(config_parser.getValue("jtag_lock_firmware") is True):
        mem_map = {**SoCCore.mem_map, **{"spiflash": 0x02000000}}
    def __init__(self, jtag_debug, no_log, sys_clk_freq=int(75e6), with_led_chaser=True, with_video_terminal=False, **kwargs):
        platform = board.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------_-----------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Basys3", **kwargs)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoVGAPHY(platform.request("vga"), clock_domain="vga")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")

        # Lock handler
        self.submodules.lock_handler = AddLockHandler(platform)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # JTAG Lock --------------------------------------------------------------------------------
        self.submodules.jtag = JTAGLock(self, platform, jtag_debug)

        # Random Generator -------------------------------------------------------------------------
        self.submodules.counter = Counter()

        self.add_csr("test")

        # Keypad Support ---------------------------------------------------------------------------
        self.submodules.keypad = Keypad(platform)
        # Flash SPI --------------------------------------------------------------------------------
        config_parser = Config.getInstance()
        if(config_parser.getValue("jtag_lock_firmware") is True):
            from litespi.modules import N25Q256A
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=N25Q256A(Codes.READ_1_1_1), with_master=False)
            self.add_constant("FLASH_BOOT_ADDRESS", 0x02000000)

        # Firmware Configuration -------------------------------------------------------------------
        if(config_parser.getValue("address_range_overlap") is True):
            self.add_constant("ADDRESS_RANGE_OVERLAP", 1)

        if(no_log is True):
            self.add_constant("CONFIG_BIOS_NO_PROMPT", 1)


# Build --------------------------------------------------------------------------------------------  
def main():

    config_parser = Config.getInstance()
    config_parser.readFile(os.path.dirname(__file__) + "/config/config.ini")

    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Basys3")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",               action="store_true", help="Build design.")
    target_group.add_argument("--load",                action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",        default=75e6,        help="System clock frequency.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",     action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",         action="store_true", help="Enable SDCard support.")
    target_group.add_argument("--sdcard-adapter",      type=str,            help="SDCard PMOD adapter (digilent or numato).")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (VGA).")
    jtagopts = target_group.add_mutually_exclusive_group()
    jtagopts.add_argument("--jtag-debug", action="store_true", help="Disable JTAG lock.")
    logopts = target_group.add_mutually_exclusive_group()
    logopts.add_argument("--no-log", action="store_true", help="Disable boot log from LiteX bios.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_video_terminal    = args.with_video_terminal,
        jtag_debug             = args.jtag_debug,
        no_log                 = args.no_log,
        **soc_core_argdict(args)
    )

    soc.platform.add_extension(board._sdcard_pmod_io)

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
