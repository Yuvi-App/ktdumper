from dump.v2.mlc_check_v2 import MlcCheck_v2
from dump.nec.nec_protocol_v2 import NecProtocol_v2
from dump.v2.rw_access_v2 import RwAccess_v2


class NecMlcCheck(MlcCheck_v2, RwAccess_v2, NecProtocol_v2):
    pass
