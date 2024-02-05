import struct

from migen import *
from migen.genlib.misc import WaitTimer

from litex.soc.interconnect.csr import *
from litex.soc.interconnect import wishbone

from litex.soc.integration.config import Config

class JTAGLock(Module, AutoCSR):
    def __init__(self, soc, platform, jtag_debug):

        config_parser = Config.getInstance()

        # Disable overlap vulnerability if flash spi vulnerability is set
        if (config_parser.getValue("jtag_lock_firmware") is True):
            config_parser.setValue('jtag_lock_overlap', 'no')
        
        # Disable normal jtag password vulnerability if variant (randoim password) is set
        if (config_parser.getValue("jtag_password_random") is True):
            config_parser.setValue('jtag_password', 'no')

         # Check if the CPU has a JTAG interface
        if soc.cpu_variant is not None and "vul" in soc.cpu_variant:

            # Request the pins on the boards necessary for the JTAG interface
            pin_tdi = platform.request("jtag_tdi")
            pin_tms = platform.request("jtag_tms")
            pin_tck = platform.request("jtag_tck")
            pin_tdo = platform.request("jtag_tdo")

            # Check if the user decide to enable JTAG interface
            # JTAG debug disable every vulnerabilities related to JTAG interface.
            if jtag_debug:

                # Disable JTAG vulnerabilities if JTAG debug is on
                config_parser.setValue('jtag_lock_overlap', 'no')
                config_parser.setValue('jtag_lock_firmware', 'no')
                config_parser.setValue('jtag_password', 'no')

                self.comb += [
                        soc.current_cpu.cpu_params["i_jtag_tdi"].eq(pin_tdi),
                        soc.current_cpu.cpu_params["i_jtag_tms"].eq(pin_tms),
                        soc.current_cpu.cpu_params["i_jtag_tck"].eq(pin_tck),
                        pin_tdo.eq(soc.current_cpu.cpu_params["o_jtag_tdo"])
                    ]

                return

            if (config_parser.getValue('jtag_lock_overlap') is True or config_parser.getValue("jtag_lock_firmware") is True) and config_parser.getValue('jtag_password') is False and config_parser.getValue('jtag_password_random') is False:
                
                # Check which vulnerability is set
                if (config_parser.getValue("jtag_lock_firmware") is True):
                    self.jtag_lock = CSRStorage(name="jtag_lock", description="JTAG Lock Control.", reset_less=True)
                else:
                    self.jtag_lock = CSRStorage(name="jtag_lock", description="JTAG Lock Control.")
                self.jtag_status = CSRStatus()
                
                # Signals used to disable JTAG
                dummy_tdi = Signal()
                dummy_tms = Signal()
                dummy_tck = Signal()

                # Logical check to enable / disable JTAG
                self.comb += [
                    If(self.jtag_lock.storage == 1,
                        soc.current_cpu.cpu_params["i_jtag_tdi"].eq(pin_tdi),
                        soc.current_cpu.cpu_params["i_jtag_tms"].eq(pin_tms),
                        soc.current_cpu.cpu_params["i_jtag_tck"].eq(pin_tck),
                        pin_tdo.eq(soc.current_cpu.cpu_params["o_jtag_tdo"])
                    ).Else(
                        dummy_tdi.eq(pin_tdi),
                        dummy_tms.eq(pin_tms),
                        dummy_tck.eq(pin_tck),
                        pin_tdo.eq(0)
                    )
                ]

                return

            if (config_parser.getValue('jtag_lock_overlap') is True or config_parser.getValue("jtag_lock_firmware") is True) and config_parser.getValue('jtag_password') is True and config_parser.getValue('jtag_password_random') is False:

                # Check which vulnerability is set
                if (config_parser.getValue("jtag_lock_firmware") is True):
                    self.jtag_lock = CSRStorage(name="jtag_lock", description="JTAG Lock Control.", reset_less=True)
                else:
                    self.jtag_lock = CSRStorage(name="jtag_lock", description="JTAG Lock Control.")
                
                # Password input from firmware
                self.jtag_password_csr = CSRStorage(size=32, name="jtag_password", description="JTAG Lock Password.", reset_less=True)

                # Memory mapped registers to check status in the firmware
                self.jtag_status = CSRStatus()
                self.password_status = CSRStatus()

                self.password = config_parser.getString("jtag_password_key")
                if(self.password is False):
                    raise ValueError("Please enter a valid password in the configuration file.")
                
                self.encoded_password = struct.unpack(">I", self.password.encode("ascii"))[0]

                # Signals used to disable JTAG
                dummy_tdi = Signal()
                dummy_tms = Signal()
                dummy_tck = Signal()

                # Logical check to enable / disable JTAG
                self.comb += [self.password_status.status.eq(1)]
                for i in range(30):
                    self.comb += [
                        If(self.jtag_lock.storage == 1,
                            self.jtag_status.status.eq(1),
                            If(self.jtag_password_csr.storage[31-i] == int(list(bin(self.encoded_password)[2:].zfill(32))[i], 2),
                                soc.current_cpu.cpu_params["i_jtag_tdi"].eq(pin_tdi),
                                soc.current_cpu.cpu_params["i_jtag_tms"].eq(pin_tms),
                                soc.current_cpu.cpu_params["i_jtag_tck"].eq(pin_tck),
                                pin_tdo.eq(soc.current_cpu.cpu_params["o_jtag_tdo"])
                            ).Else(
                                dummy_tdi.eq(pin_tdi),
                                dummy_tms.eq(pin_tms),
                                dummy_tck.eq(pin_tck),
                                pin_tdo.eq(0),
                                self.password_status.status.eq(0)
                            )
                        ).Else(
                            dummy_tdi.eq(pin_tdi),
                            dummy_tms.eq(pin_tms),
                            dummy_tck.eq(pin_tck),
                            pin_tdo.eq(0),
                            self.jtag_status.status.eq(0),
                            self.password_status.status.eq(0)
                        )
                    ]

                return

            if config_parser.getValue('jtag_lock_overlap') is False and config_parser.getValue("jtag_lock_firmware") is False and config_parser.getValue('jtag_password') is True and config_parser.getValue('jtag_password_random') is False:

                # Password input from firmware and status
                self.jtag_password_csr = CSRStorage(size=32, name="jtag_password", description="JTAG Lock Password.", reset_less=True)
                self.password_status = CSRStatus()

                self.password = config_parser.getString("jtag_password_key")
                if(self.password is False):
                    raise ValueError("Please enter a valid password in the configuration file.")
                
                self.encoded_password = struct.unpack(">I", self.password.encode("ascii"))[0]

                # Signals used to disable JTAG
                dummy_tdi = Signal()
                dummy_tms = Signal()
                dummy_tck = Signal()

                # Logical check to enable / disable JTAG
                self.comb += [self.password_status.status.eq(1)]
                for i in range(30):
                    self.comb += [
                        If(self.jtag_password_csr.storage[31-i] == int(list(bin(self.encoded_password)[2:].zfill(32))[i], 2),
                            soc.current_cpu.cpu_params["i_jtag_tdi"].eq(pin_tdi),
                            soc.current_cpu.cpu_params["i_jtag_tms"].eq(pin_tms),
                            soc.current_cpu.cpu_params["i_jtag_tck"].eq(pin_tck),
                            pin_tdo.eq(soc.current_cpu.cpu_params["o_jtag_tdo"]),
                        ).Else(
                            dummy_tdi.eq(pin_tdi),
                            dummy_tms.eq(pin_tms),
                            dummy_tck.eq(pin_tck),
                            pin_tdo.eq(0),
                            self.password_status.status.eq(0)
                        )
                    ]

                return

            if config_parser.getValue('jtag_lock_overlap') is False and config_parser.getValue("jtag_lock_firmware") is False and config_parser.getValue('jtag_password') is False and config_parser.getValue('jtag_password_random') is True:

                # Password input from firmware and lock password set by the firmware randomly
                self.jtag_password_csr = CSRStorage(size=32, name="jtag_password", description="JTAG Lock Password.")
                self.jtag_password_csr_soft = CSRStorage(size=32, name="jtag_password_soft", description="JTAG Lock Password set by the software.")

                # Status to check password verification from the firmware
                self.password_status = CSRStatus()

                # Signals used to disable JTAG
                dummy_tdi = Signal()
                dummy_tms = Signal()
                dummy_tck = Signal()

                # Logical check to enable / disable JTAG
                self.comb += [self.password_status.status.eq(1)]
                for i in range(30):
                    self.comb += [
                        If(self.jtag_password_csr.storage[i] == self.jtag_password_csr_soft.storage[i],
                            soc.current_cpu.cpu_params["i_jtag_tdi"].eq(pin_tdi),
                            soc.current_cpu.cpu_params["i_jtag_tms"].eq(pin_tms),
                            soc.current_cpu.cpu_params["i_jtag_tck"].eq(pin_tck),
                            pin_tdo.eq(soc.current_cpu.cpu_params["o_jtag_tdo"]),
                        ).Else(
                            dummy_tdi.eq(pin_tdi),
                            dummy_tms.eq(pin_tms),
                            dummy_tck.eq(pin_tck),
                            pin_tdo.eq(0),
                            self.password_status.status.eq(0)
                        )
                    ]

                return

            if (config_parser.getValue('jtag_lock_overlap') is True or config_parser.getValue("jtag_lock_firmware") is True) and config_parser.getValue('jtag_password') is False and config_parser.getValue('jtag_password_random') is True:

                # Check which vulnerability is set
                if (config_parser.getValue("jtag_lock_firmware") is True):
                    self.jtag_lock = CSRStorage(name="jtag_lock", description="JTAG Lock Control.", reset_less=True)
                else:
                    self.jtag_lock = CSRStorage(name="jtag_lock", description="JTAG Lock Control.")
                
                # Password input from firmware and lock password set by the firmware randomly
                self.jtag_password_csr = CSRStorage(size=32, name="jtag_password", description="JTAG Lock Password.")
                self.jtag_password_csr_soft = CSRStorage(size=31, name="jtag_password_soft", description="JTAG Lock Password set by the software.")

                # Memory mapped registers to check status in the firmware
                self.jtag_status = CSRStatus()
                self.password_status = CSRStatus()

                # Signals used to disable JTAG
                dummy_tdi = Signal()
                dummy_tms = Signal()
                dummy_tck = Signal()

                # Logical check to enable / disable JTAG
                self.comb += [self.password_status.status.eq(1)]
                for i in range(30):
                    self.comb += [
                        If(self.jtag_lock.storage == 1,
                            self.jtag_status.status.eq(1),
                            If(self.jtag_password_csr.storage[i] == self.jtag_password_csr_soft.storage[i],
                                soc.current_cpu.cpu_params["i_jtag_tdi"].eq(pin_tdi),
                                soc.current_cpu.cpu_params["i_jtag_tms"].eq(pin_tms),
                                soc.current_cpu.cpu_params["i_jtag_tck"].eq(pin_tck),
                                pin_tdo.eq(soc.current_cpu.cpu_params["o_jtag_tdo"])
                            ).Else(
                                dummy_tdi.eq(pin_tdi),
                                dummy_tms.eq(pin_tms),
                                dummy_tck.eq(pin_tck),
                                pin_tdo.eq(0),
                                self.password_status.status.eq(0)
                            )
                        ).Else(
                            dummy_tdi.eq(pin_tdi),
                            dummy_tms.eq(pin_tms),
                            dummy_tck.eq(pin_tck),
                            pin_tdo.eq(0),
                            self.jtag_status.status.eq(0),
                            self.password_status.status.eq(0)
                        )
                    ]

                return