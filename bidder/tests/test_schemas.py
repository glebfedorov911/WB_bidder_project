from unittest.mock import patch
import unittest

from bidder.schemas import TypeCampaign
from bidder.exception import *


class TestTypeCampaign(unittest.TestCase):

    def setUp(self):
        self.automatic = 'automatic'
        self.automatic_type = TypeCampaign.AUTOMATIC

        self.automatic_wb_code = 8
        self.automatic_bad_wb_code = 10

    def test_type_campaign(self):
        type_campaign_good_data = self._given_data()

        result = self._when_result(data=type_campaign_good_data)

        self._then_assert(result=result, wb_code=self.automatic_wb_code, type=self.automatic_type)

    def _given_data(self) -> str:
        return self.automatic

    def _when_result(self, data: str) -> str:
        return TypeCampaign(data)

    def _then_assert(self, result: str, wb_code: str, type: TypeCampaign) -> None:
        self.assertEqual(result.wb_code, wb_code)
        self.assertEqual(result, type)