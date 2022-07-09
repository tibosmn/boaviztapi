import pandas as pd

from boaviztapi.model.boattribute import Boattribute, Status

_electricity_emission_factors_df = pd.read_csv('./boaviztapi/data/electricity/electricity_impact_factors.csv')

_cpu_profile_file = './boaviztapi/data/consumption_profile/cpu/cpu_profile.csv'
_cloud_profile_file = './boaviztapi/data/consumption_profile/cloud/cpu_profile.csv'
_server_profile_file = './boaviztapi/data/consumption_profile/server/server_profile.csv'


class ModelUsage:
    DEFAULT_USAGE_LOCATION = "EEE"
    DEFAULT_USE_TIME_IN_HOURS = 24 * 365
    DEFAULT_LIFE_TIME_IN_HOURS = 24 * 365 * 3  # 3 years
    DEFAULT_WORKLOAD = 50.

    _DAYS_IN_HOURS = 24
    _YEARS_IN_HOURS = 24 * 365

    def __init__(self, /, **kwargs):
        self.hours_electrical_consumption = Boattribute(value=None, status=Status.NONE, unit="W", default=0)
        self.workload = None
        self.usage_location = Boattribute(value=None, status=Status.NONE, unit="CodSP3 - NCS Country Codes - NATO",
                                          default=self.DEFAULT_USAGE_LOCATION)
        self.adp_factor = Boattribute(value=None, status=Status.NONE, unit="kgCO2e/kWh",
                                      default=default_impact_factor, args={"impact_type": "adpe",
                                                                           "usage_location": self.usage_location,
                                                                           "emission_factors_df": _electricity_emission_factors_df})
        self.gwp_factor = Boattribute(value=None, status=Status.NONE, unit="KgSbeq/kWh", default=default_impact_factor,
                                      args={"impact_type": "gwp",
                                            "usage_location": self.usage_location,
                                            "emission_factors_df": _electricity_emission_factors_df})
        self.pe_factor = Boattribute(value=None, status=Status.NONE, unit="MJ/kWh", default=default_impact_factor,
                                     args={"impact_type": "pe",
                                           "usage_location": self.usage_location,
                                           "emission_factors_df": _electricity_emission_factors_df})

        self.use_time = Boattribute(value=None, status=Status.NONE, unit="hours",
                                    default=self.DEFAULT_USE_TIME_IN_HOURS)
        self.life_time = Boattribute(value=None, status=Status.NONE, unit="hours",
                                     default=self.DEFAULT_LIFE_TIME_IN_HOURS)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


class ModelUsageServer(ModelUsage):
    DEFAULT_OTHER_CONSUMPTION_RATIO = 0.33
    DEFAULT_LIFE_TIME_IN_HOURS = 24 * 365 * 3  # 3 years

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        self._other_consumption_ratio = Boattribute(value=None, status=Status.NONE, unit="ratio /1")

        for attr, val in kwargs.items():
            if val is not None:
                self.__setattr__(attr, val)

    @property
    def other_consumption_ratio(self) -> float:
        if self._other_consumption_ratio.value is None:
            self._other_consumption_ratio.value = self.DEFAULT_OTHER_CONSUMPTION_RATIO
            self._other_consumption_ratio.status = Status.DEFAULT
        return self._other_consumption_ratio.value

    @other_consumption_ratio.setter
    def other_consumption_ratio(self, value: float) -> None:
        self._other_consumption_ratio.value = value


class ModelUsageCloud(ModelUsageServer):
    DEFAULT_INSTANCE_PER_SERVER = 1
    DEFAULT_LIFE_TIME_IN_HOURS = 24 * 365 * 2  # 2 years

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        self.__instance_per_server = self.DEFAULT_INSTANCE_PER_SERVER

        for attr, val in kwargs.items():
            if val is not None:
                self.__setattr__(attr, val)

    @property
    def instance_per_server(self) -> int:
        return self.__instance_per_server

    @instance_per_server.setter
    def instance_per_server(self, value: int) -> None:
        self.__instance_per_server = value


def default_impact_factor(args):
    sub = args["emission_factors_df"]
    sub = sub[sub['code'] == args["usage_location"].value]
    return float(sub[f"{args['impact_type']}_emission_factor"]), sub[f"{args['impact_type']}_emission_source"], Status.COMPLETED
