from unittest.mock import patch
import unittest

from ..schemas import TypeCampaign
from utils.exceptions import *


class TestTypeCampaign(unittest.TestCase):

    def setUp(self):
        self.automatic = 'automatic'
        self.automatic_type = TypeCampaign.AUTOMATIC
        self.automatic_wb_code = 8

        self.bad_data = "test"
        self.automatic_bad_wb_code = 10

    def test_type_campaign(self):
        type_campaign_good_data = self._given_data()

        result = self._when_result(data=type_campaign_good_data)

        self._then_assert(result=result, wb_code=self.automatic_wb_code, type=self.automatic_type)
   
    def test_type_data_not_in_list(self):
        type_campaign_bad_data = self._given_bad_data()

        exception = self._when_exception(data=type_campaign_bad_data, exception=ValueError)

        self._then_assert_attribute(result=exception)

    def _given_data(self) -> str:
        return self.automatic

    def _given_bad_data(self) -> str:
        return self.bad_data 

    def _when_result(self, data: str) -> str:
        return TypeCampaign(data)

    def _when_exception(self, data, exception) -> str:
        with self.assertRaises(exception) as context:
            self._when_result(data=data)

        return str(context.exception)

    def _then_assert(self, result: str, wb_code: str, type: TypeCampaign) -> None:
        self.assertEqual(result.wb_code, wb_code)
        self.assertEqual(result, type)

    def _then_assert_attribute(self, result: str) -> None:
        self.assertIn(self.bad_data, result)
        self.assertIn("TypeCampaign", result)


class TestBidderData(unittest.TestCase):
    ...
    #TODO: Сделать тесты для разных ставок