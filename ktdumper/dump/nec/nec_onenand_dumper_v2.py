from dump.common.common_onenand_dumper import CommonOnenandDumper
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.nec.nec_protocol_v2 import NecProtocol_v2


class NecOnenandDumper_v2(CommonOnenandDumper, RwAccess_v2, NecProtocol_v2):
    pass
