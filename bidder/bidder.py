from .schemas import BidderData, CPMChangeSchema, TypeCampaign
from .exception import *

import httpx


class Bidder:
    def __init__(self, bidder_data: BidderData, cpm_change: CPMChangeSchema):
        super().__init__()
        
        self.__dict__.update(vars(bidder_data))
        self.__dict__.update(vars(cpm_change))

        self.type = self._get_wb_code_for_type(wb_type=cpm_change.type)

    def _get_wb_code_for_type(self, wb_type: TypeCampaign) -> int:
        if not hasattr(wb_type, "wb_code"):
            raise ValueError(INVALID_CAMPAIGN_TYPE_WB_CODE_MISSING)
        return wb_type.wb_code

    