from utils.exceptions import (
    CANNOT_COLLECT, CANNOT_GET_VAR_NAME
)

import numpy as np
import sqlite3
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error 
import xgboost as xgb
import inspect

from abc import ABC, abstractmethod, abstractstaticmethod
import re


class Cleaner(ABC):

    @abstractstaticmethod
    def clean(value):
        ...

class Prepare(ABC):

    @abstractmethod
    def get_data(self) -> list:
        ...

class CleanerProcess:

    def get_methods(self, obj: object, method: str | None, value: str):
        if method:
            return obj.__dict__[method](value)
        return value

class NeuroCleaner(Cleaner, CleanerProcess):
    FUNC_INDEXES = {
        '0': "_clean_from_value",
        '1': "_clean_price",
        '3': "_clean_marks",
        '4': "_clean_count_marks",
        '5': "_clean_fbo",
        '6': "_clean_num_of_the_rating",
    }

    def clean(self, index, value):
        return self.get_methods(self.__class__, method=self.FUNC_INDEXES.get(str(index)), value=value)

    @staticmethod
    def _clean_from_value(value) -> int:
        value = str(value).replace("\xa0", '').split(" ")[1]
        return int(value)

    @staticmethod
    def _clean_price(value):
        value = str(value).replace("\xa0", '').replace(r"\xa0", '')
        value = value.split(" ")[1]
        return int(value)

    @staticmethod
    def _clean_marks(value):
        value = str(value).replace(",", ".").replace("\xa0", '')
        return float(value) if value else 0.0

    @staticmethod
    def _clean_count_marks(value):
        value = str(value).replace("\xa0", '')
        value = value.split(" ")[0]
        return int(value) if value.lower() != "нет" else 0.0

    @staticmethod
    def _clean_fbo(value):
        match = re.search(r'\d[\d\s]*\d|\b0\b', value)
        result = match.group().replace(' ', '') if match else '0'
        return int(result)

    @staticmethod
    def _clean_num_of_the_rating(value):
        return int(value)
    
class DataPrepare(Prepare):

    def __init__(self, parsed_data: list[tuple], cleaner: Cleaner = NeuroCleaner()):
        self.parsed_data = parsed_data
        self.len_one_collection_data = len(self.parsed_data[0]) \
            if len(self.parsed_data) > 0 \
            else 0
            
        self.cleaner = cleaner

    def get_data(self) -> list[np.array]:
        results = self._prepare_for_numpy()

        return [np.array(result) for result in results]

    def _prepare_for_numpy(self) -> list[list]:
        results = self._prepare_list_for_results()
        
        return self._collect_data(results=results)

    def _prepare_list_for_results(self) -> list[list]:
        return [[] for _ in range(self.len_one_collection_data)]
    
    def _collect_data(self, results: list[list]) -> list[list]:
        for data in self.parsed_data:
            results = self._collect_data_to_results(data=data, results=results)

        return results

    def _collect_data_to_results(self, data: tuple, results: list[list]) -> list[list]:
        try:
            for i in range(self.len_one_collection_data):
                value = self._try_convert_float(data[i])

                results[i].append(self.cleaner.clean(i, value))
        except Exception as e:
            raise(e)
            ValueError(CANNOT_COLLECT)
        
        return results

    def _try_convert_float(self, value) -> str | float:
        try:
            value = float(value)
        except:
            ...
        return value

class INeuroAnalytics(ABC):

    @abstractmethod
    def start(self):
        ...

class NeuroAnalytics(INeuroAnalytics):
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    MINIMUM_RESHAPE = -1
    MAXIMUM_RESHAPE = 1
    PARAMS = {
        "objective": "reg:squarederror", 
        "max_depth": 6,  
        "eta": 0.1,
        "eval_metric": "rmse", 
    }
    NUM_ROUNDS = 100
    EARLY_STOPPING_ROUNDS = 10

    def __init__(
        self,
        prepare: Prepare,
    ):
        self.prepare = prepare
        self.form_values, self.prices, self.queries, self.marks, \
            self.count_marks, self.fbo, self.num_of_the_rating = self.prepare.get_data()

    def start(self):
        self._normalize_data()
        X, y = self._combining_features()

        x_train, x_test, y_train, y_test = self._train_data(x=X, y=y)
        dtrain, dtest = self._to_xgboost(x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test) 

        evals = [(dtrain, "train"), (dtest, "eval")]
        model = xgb.train(self.PARAMS, dtrain, self.NUM_ROUNDS, evals, early_stopping_rounds=self.EARLY_STOPPING_ROUNDS)

        y_pred = self._predict(model, dtest)
        return y_pred[:5]

    def _normalize_data(self) -> None:
        scaler = StandardScaler()
        reshape_tuple = (self.MINIMUM_RESHAPE, self.MAXIMUM_RESHAPE)

        self.form_values = self._fit_transform(scaler=scaler, value=self.form_values, reshape_tuple=reshape_tuple)
        self.num_of_the_rating = self._fit_transform(scaler=scaler, value=self.num_of_the_rating, reshape_tuple=reshape_tuple)
        self.marks = self._fit_transform(scaler=scaler, value=self.marks, reshape_tuple=reshape_tuple)
        self.count_marks = self._fit_transform(scaler=scaler, value=self.count_marks, reshape_tuple=reshape_tuple)
        self.fbo = self._fit_transform(scaler=scaler, value=self.fbo, reshape_tuple=reshape_tuple)

    def _fit_transform(self, scaler: StandardScaler, value: np.array, reshape_tuple: tuple):
        return scaler.fit_transform(value.reshape(reshape_tuple))

    def _combining_features(self) -> tuple:
        X = self._x_concatenate()
        y = self.prices

        return X, y

    def _x_concatenate(self):
        return np.concatenate([
            self.form_values, self.num_of_the_rating, self.marks, self.count_marks, self.fbo
        ], axis=1)

    def _train_data(self, x, y) -> tuple:
        return train_test_split(
            x, y, test_size=self.TEST_SIZE, random_state=self.RANDOM_STATE
        )

    def _to_xgboost(self, x_train, x_test, y_train, y_test) -> tuple:
        dtrain = self._to_dmatrix(x=x_train, y=y_train)
        dtest = self._to_dmatrix(x=x_test, y=y_test)

        return dtrain, dtest

    def _to_dmatrix(self, x, y):
        return xgb.DMatrix(x, y)

    def _predict(self, model, dtest):
        return model.predict(dtest)