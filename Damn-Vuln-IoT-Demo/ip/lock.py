from migen import *
from litex.soc.interconnect.csr import *
from litex.soc.cores.gpio import GPIOIn, GPIOOut
from litex.soc.integration.config import Config


class Contents:
    def __init__(self):
        self.FLAG = [0x47414c46, 0x44203a20, 0x6d7b5356, 0x526f6d45, 0x61566f59, 0x50614c72, 0x0000007d] # "FLAG : DVS{mEmoRYoVarLaP}"
        self.PADDING = [0x00000000] 
        self.USERNAME = [0x494d4441, 0x5355204e, 0x414e5245, 0x3a20454d, 0x6d646120, 0x00006e69] # "ADMIN USERNAME : admin"
        self.PASSWORD = [0x494d4441, 0x4150204e, 0x4f575353, 0x3a204452, 0x73617020, 0x726f7773, 0x00000064] # "ADMIN PASSWORD : password"
        self.TOP_SECRET_PASSWORD_ACCESS = [0x20504f54, 0x20434553, 0x53534150, 0x44524f57, 0x30203a20, 0x61656478, 0x65656264, 0x00000066] # "TOP SEC PASSWORD : 0xdeadbeef"

class AddLockHandler(Module, AutoCSR, Contents):
    def __init__(self, platform=None):
        config_parser = Config.getInstance()
        if config_parser.getValue("loop_back_signal") and (platform != None):
            Contents.__init__(self)
            self.loop_back_signal = GPIOIn(platform.request("loop_back_signal", 0))
            self.submodules += ClockDomainsRenamer("sys")(self.loop_back_signal)

            self.output_signal = GPIOOut(platform.request("output_signal", 0))
            self.submodules += ClockDomainsRenamer("sys")(self.output_signal)

            self.lock_error = CSRStorage(16, description="Lock error", write_from_dev=True)

            self.sync += self.lock_error.storage.eq(self.loop_back_signal._in.status != self.output_signal.out.storage)