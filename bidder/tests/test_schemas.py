from pydantic import BaseModel

from unittest.mock import patch
import unittest

from ..schemas import TypeCampaign, BidderData, ModeBidder
from utils.exceptions import *
from ..settings import settings 


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
    
    def setUp(self):
        self.max_cpm_campaign_good = 10000
        self.min_cpm_campaign_good = 1000

        self.max_cpm_campaign_bad_smaller_then_min = 1
        self.min_cpm_campaign_bad_biggest_then_max = 1000

        self.max_cpm_campaign_bad_smaller_than_default_cpm = 10
        self.min_cpm_campaign_bad_smaller_than_default_cpm = 9

        self.wish_place_in_top = 2
        self.type_work_bidder = "default"
        self.step = 5
        self.advertId = 1234
        self.type = "automatic"
        
        self.default_cpm = settings.cpm_var.min_cpm

        self.bad_type_work_bidder = "test"

        self.min_max_cpm_exception = "Min CPM cannot be greather then Max CPM"

    def test_good_data(self):
        bidder_data = self._given_data(
            mx_cpm=self.max_cpm_campaign_good, 
            mn_cpm=self.min_cpm_campaign_good,
            type_work=self.type_work_bidder
        )

        result = self._when_model_dump_data(data=bidder_data)

        data_to_check = {
            "advertId": self.advertId,
            "type": TypeCampaign(self.type),
            "max_cpm_campaign": self.max_cpm_campaign_good,
            "min_cpm_campaign": self.min_cpm_campaign_good,
            "wish_place_in_top": self.wish_place_in_top,
            "type_work_bidder": ModeBidder(self.type_work_bidder),
            "step": self.step
        }
        self._then_assert(result, data_to_check)

    def test_bad_data_cpm_smaller(self):
        exception = self._when_exception(
            exception=ValueError, 
            mx_cpm=self.max_cpm_campaign_bad_smaller_then_min,
            mn_cpm=self.min_cpm_campaign_bad_biggest_then_max,
            type_work=self.type_work_bidder
        )

        self._then_exception(msg=self.min_max_cpm_exception, result=exception)

    def test_bad_data_cpm_smaller_then_default_cpm(self):
        data = self._given_data(
            mn_cpm=self.min_cpm_campaign_bad_smaller_than_default_cpm,
            mx_cpm=self.max_cpm_campaign_bad_smaller_than_default_cpm,
            type_work=self.type_work_bidder
        )

        max_cpm, min_cpm = data.max_cpm_campaign, data.min_cpm_campaign

        self._then_assert(max_cpm, self.default_cpm)
        self._then_assert(min_cpm, self.default_cpm)

    # def test_bad_type_work_bidder(self):
    #     data = self._given_data(
    #         mn_cpm=self.min_cpm_campaign_good,
    #         mx_cpm=self.max_cpm_campaign_good,
    #         type_work=self.bad_type_work_bidder
    #     )

    #TODO: ПРОТЕСТИТЬ ЕЩЕ ОСАТЛЬНЫЕ КЛАССЫ И bad_type_work_bidder

    def _given_data(self, mx_cpm: int, mn_cpm: int, type_work: str) -> BidderData:
        return BidderData(
            max_cpm_campaign=mx_cpm,
            min_cpm_campaign=mn_cpm,
            wish_place_in_top=self.wish_place_in_top,
            type_work_bidder=type_work,
            step=self.step,
            advertId=self.advertId,
            type=self.type
        )

    def _when_model_dump_data(self, data: BaseModel) -> dict:
        return data.model_dump()

    def _when_exception(self, exception: str, **kwargs) -> str:
        with self.assertRaises(exception) as context:
            self._given_data(**kwargs)

        return str(context.exception)

    def _then_assert(self, result: dict, data: dict) -> None:
        self.assertEqual(result, data)

    def _then_exception(self, msg: str, result: str) -> None:
        self.assertIn(msg, result)