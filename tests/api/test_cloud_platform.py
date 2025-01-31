import pytest
from httpx import AsyncClient, ASGITransport

from boaviztapi.main import app

from dataclasses import dataclass
from .util import (
    CloudPlatformRequest,
    ADPImpact,
    GWPImpact,
    PEImpact,
    ImpactOutput,
    END_OF_LIFE_WARNING,
    UNCERTAINTY_WARNING,
)

pytest_plugins = ("pytest_asyncio",)


@dataclass
class CloudPlatformTest:
    request: CloudPlatformRequest

    adp: ADPImpact
    gwp: GWPImpact
    pe: PEImpact

    verbose_output: str = None

    async def check_result(self):
        url = self.request.to_url()
        body = self.request.to_dict()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            if self.request.use_url_params:
                res = await ac.get(url)
            else:
                res = await ac.post(url, json=body)

        expected = {
            "impacts": {
                "adp": self.adp.to_dict(),
                "gwp": self.gwp.to_dict(),
                "pe": self.pe.to_dict(),
            },
        }

        assert res.json() == expected


@pytest.mark.asyncio
async def test_empty_usage():
    test = CloudPlatformTest(
        CloudPlatformRequest("aws", "a1.metal"),
        ADPImpact(
            manufacture=ImpactOutput(0.1414, 0.06512, 0.099, END_OF_LIFE_WARNING),
            use=ImpactOutput(0.0007552, 2.815e-05, 0.00015),
        ),
        GWPImpact(
            manufacture=ImpactOutput(635.6, 258.0, 450.0, END_OF_LIFE_WARNING),
            use=ImpactOutput(2559, 49.05, 900.0),
        ),
        PEImpact(
            manufacture=ImpactOutput(8833.0, 3529.0, 6300.0, END_OF_LIFE_WARNING),
            use=ImpactOutput(1331000.0, 27.72, 30000.0, UNCERTAINTY_WARNING),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_empty_usage_m6gmetal():
    test = CloudPlatformTest(
        CloudPlatformRequest("aws", "m6g.metal"),
        ADPImpact(
            manufacture=ImpactOutput(0.1741, 0.0812, 0.12, END_OF_LIFE_WARNING),
            use=ImpactOutput(0.00358, 0.0001334, 0.0007),
        ),
        GWPImpact(
            manufacture=ImpactOutput(1427.0, 504.3, 880.0, END_OF_LIFE_WARNING),
            use=ImpactOutput(12130, 232.5, 4000.0),
        ),
        PEImpact(
            manufacture=ImpactOutput(18680.0, 6649.0, 12000.0, END_OF_LIFE_WARNING),
            use=ImpactOutput(6310000.0, 131.4, 100000.0),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_empty_usage_with_url_params_a1():
    test = CloudPlatformTest(
        CloudPlatformRequest("aws", "a1.metal", use_url_params=True),
        ADPImpact(
            ImpactOutput(0.1414, 0.06512, 0.099, END_OF_LIFE_WARNING),
            ImpactOutput(0.0007552, 2.815e-05, 0.00015),
        ),
        GWPImpact(
            ImpactOutput(635.6, 258.0, 450.0, END_OF_LIFE_WARNING),
            ImpactOutput(2559.0, 49.05, 900.0),
        ),
        PEImpact(
            ImpactOutput(8833.0, 3529.0, 6300.0, END_OF_LIFE_WARNING),
            ImpactOutput(1331000.0, 27.72, 30000.0, UNCERTAINTY_WARNING),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_empty_usage_with_url_params_r5ad():
    test = CloudPlatformTest(
        CloudPlatformRequest("aws", "r5ad.24xlarge", use_url_params=True),
        ADPImpact(
            ImpactOutput(0.2801, 0.1487, 0.2, END_OF_LIFE_WARNING),
            ImpactOutput(0.01002, 0.0003733, 0.002),
        ),
        GWPImpact(
            ImpactOutput(3510.0, 1244.0, 2100.0, END_OF_LIFE_WARNING),
            ImpactOutput(33940.0, 650.5, 12000.0),
        ),
        PEImpact(
            ImpactOutput(44690.0, 16000.0, 26000.0, END_OF_LIFE_WARNING),
            ImpactOutput(17650000.0, 367.7, 400000.0, UNCERTAINTY_WARNING),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_wrong_input():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/v1/cloud/platform?verbose=false",
            json={"provider": "test", "platform_type": "a1.4xlarge", "usage": {}},
        )
    assert res.json() == {"detail": "a1.4xlarge at test not found"}


@pytest.mark.asyncio
async def test_wrong_input_1():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/v1/cloud/platform?verbose=false",
            json={"provider": "aws", "platform_type": "test", "usage": {}},
        )
    assert res.json() == {"detail": "test at aws not found"}


@pytest.mark.asyncio
async def test_usage_with_complex_time_workload():
    test = CloudPlatformTest(
        CloudPlatformRequest(
            "aws",
            "c5a.24xlarge",
            usage={
                "time_workload": [
                    {"time_percentage": 50, "load_percentage": 0},
                    {"time_percentage": 25, "load_percentage": 60},
                    {"time_percentage": 25, "load_percentage": 100},
                ]
            },
        ),
        ADPImpact(
            ImpactOutput(0.1744, 0.08626, 0.124, END_OF_LIFE_WARNING),
            ImpactOutput(0.003867, 0.0001442, 0.0008),
        ),
        GWPImpact(
            ImpactOutput(1215.0, 458.4, 780.0, END_OF_LIFE_WARNING),
            ImpactOutput(13110.0, 251.2, 5000.0),
        ),
        PEImpact(
            ImpactOutput(16070.0, 6108.0, 10500.0, END_OF_LIFE_WARNING),
            ImpactOutput(6817000.0, 142.0, 200000.0),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_usage_with_simple_time_workload():
    test = CloudPlatformTest(
        CloudPlatformRequest(
            "aws",
            "c5a.24xlarge",
            usage={"time_workload": 100},
        ),
        ADPImpact(
            ImpactOutput(0.1744, 0.08626, 0.124, END_OF_LIFE_WARNING),
            ImpactOutput(0.006589, 0.0002456, 0.0013),
        ),
        GWPImpact(
            ImpactOutput(1215.0, 458.4, 780.0, END_OF_LIFE_WARNING),
            ImpactOutput(22330.0, 427.9, 8000.0),
        ),
        PEImpact(
            ImpactOutput(16070.0, 6108.0, 10500.0, END_OF_LIFE_WARNING),
            ImpactOutput(11610000.0, 241.9, 300000.0, UNCERTAINTY_WARNING),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_usage_with_duration():
    test = CloudPlatformTest(
        CloudPlatformRequest(
            "aws",
            "c5a.24xlarge",
            duration=1,
        ),
        ADPImpact(
            ImpactOutput(4.977e-06, 2.462e-06, 3.5e-06, END_OF_LIFE_WARNING),
            ImpactOutput(1.459e-07, 5.437e-09, 3e-08),
        ),
        GWPImpact(
            ImpactOutput(0.03467, 0.01308, 0.022, END_OF_LIFE_WARNING),
            ImpactOutput(0.4942, 0.009473, 0.17),
        ),
        PEImpact(
            ImpactOutput(0.4588, 0.1743, 0.3, END_OF_LIFE_WARNING),
            ImpactOutput(257.1, 0.005354, 10.0),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_usage_with_duration_and_time_workload():
    test = CloudPlatformTest(
        CloudPlatformRequest(
            "aws",
            "a1.metal",
            duration=2,
            usage={
                "usage_location": "FRA",
                "time_workload": [
                    {"time_percentage": "50", "load_percentage": "0"},
                    {"time_percentage": "50", "load_percentage": "50"},
                ],
            },
        ),
        ADPImpact(
            ImpactOutput(8.07e-06, 3.717e-06, 5.6e-06, END_OF_LIFE_WARNING),
            ImpactOutput(5.343e-09, 4.007e-09, 4.4e-09),
        ),
        GWPImpact(
            ImpactOutput(0.03628, 0.01472, 0.026, END_OF_LIFE_WARNING),
            ImpactOutput(0.01078, 0.008083, 0.009),
        ),
        PEImpact(
            ImpactOutput(0.5041, 0.2014, 0.36, END_OF_LIFE_WARNING),
            ImpactOutput(1.242, 0.9312, 1.03),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_verbose_output_with_empty_usage():
    test = CloudPlatformTest(
        CloudPlatformRequest("aws", "r5ad.24xlarge", use_url_params=True),
        ADPImpact(
            ImpactOutput(0.2801, 0.1487, 0.2, END_OF_LIFE_WARNING),
            ImpactOutput(0.01002, 0.0003733, 0.002),
        ),
        GWPImpact(
            ImpactOutput(3510.0, 1244.0, 2100.0, END_OF_LIFE_WARNING),
            ImpactOutput(33940.0, 650.5, 12000.0),
        ),
        PEImpact(
            ImpactOutput(44690.0, 16000.0, 26000.0, END_OF_LIFE_WARNING),
            ImpactOutput(17650000.0, 367.7, 400000.0, UNCERTAINTY_WARNING),
        ),
        verbose_output={
            "ASSEMBLY-1": {
                "duration": {"unit": "hours", "value": 35040.0},
                "impacts": {
                    "adp": {
                        "description": "Use of minerals and fossil ressources",
                        "embedded": {
                            "max": 5.288e-07,
                            "min": 5.288e-07,
                            "value": 5.288e-07,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgSbeq",
                        "use": "not implemented",
                    },
                    "gwp": {
                        "description": "Total climate change",
                        "embedded": {
                            "max": 2.505,
                            "min": 2.505,
                            "value": 2.505,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgCO2eq",
                        "use": "not implemented",
                    },
                    "pe": {
                        "description": "Consumption of primary energy",
                        "embedded": {
                            "max": 25.72,
                            "min": 25.72,
                            "value": 25.72,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "MJ",
                        "use": "not implemented",
                    },
                },
                "units": {"max": 1, "min": 1, "status": "ARCHETYPE", "value": 1},
            },
            "CASE-1": {
                "case_type": {"status": "ARCHETYPE", "value": "rack"},
                "duration": {"unit": "hours", "value": 35040.0},
                "impacts": {
                    "adp": {
                        "description": "Use of minerals and fossil ressources",
                        "embedded": {
                            "max": 0.01038,
                            "min": 0.007575,
                            "value": 0.0076,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgSbeq",
                        "use": "not implemented",
                    },
                    "gwp": {
                        "description": "Total climate change",
                        "embedded": {
                            "max": 56.25,
                            "min": 32.21,
                            "value": 56.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgCO2eq",
                        "use": "not implemented",
                    },
                    "pe": {
                        "description": "Consumption of primary energy",
                        "embedded": {
                            "max": 825.0,
                            "min": 460.8,
                            "value": 820.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "MJ",
                        "use": "not implemented",
                    },
                },
                "units": {"max": 1, "min": 1, "status": "ARCHETYPE", "value": 1},
            },
            "CPU-1": {
                "adp_factor": {
                    "max": 2.656e-07,
                    "min": 1.32e-08,
                    "source": "ADEME Base IMPACTS ®",
                    "status": "DEFAULT",
                    "unit": "kg Sbeq/kWh",
                    "value": 6.42e-08,
                },
                "avg_power": {
                    "max": 112.22999999999999,
                    "min": 112.22999999999999,
                    "status": "COMPLETED",
                    "unit": "W",
                    "value": 112.22999999999999,
                },
                "core_units": {
                    "max": 32,
                    "min": 32,
                    "source": "Completed from name name based on "
                    "https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=224728652.",
                    "status": "COMPLETED",
                    "value": 32,
                },
                "die_size": {
                    "max": 213.0,
                    "min": 213.0,
                    "source": "Average value of Naples with 32 cores",
                    "status": "COMPLETED",
                    "unit": "mm2",
                    "value": 213.0,
                },
                "duration": {"unit": "hours", "value": 35040.0},
                "family": {
                    "max": "Naples",
                    "min": "Naples",
                    "source": "Completed from name name based on "
                    "https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=224728652.",
                    "status": "COMPLETED",
                    "value": "Naples",
                },
                "gwp_factor": {
                    "max": 0.9,
                    "min": 0.023,
                    "source": "https://www.sciencedirect.com/science/article/pii/S0306261921012149: \n"
                    "Average of 27 european countries",
                    "status": "DEFAULT",
                    "unit": "kg CO2eq/kWh",
                    "value": 0.38,
                },
                "hours_life_time": {
                    "max": 35040.0,
                    "min": 35040.0,
                    "source": "from device",
                    "status": "COMPLETED",
                    "unit": "hours",
                    "value": 35040.0,
                },
                "impacts": {
                    "adp": {
                        "description": "Use of minerals and fossil ressources",
                        "embedded": {
                            "max": 0.0153,
                            "min": 0.0153,
                            "value": 0.0153,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgSbeq",
                        "use": {"max": 0.002089, "min": 0.0001038, "value": 0.0005},
                    },
                    "gwp": {
                        "description": "Total climate change",
                        "embedded": {
                            "max": 10.73,
                            "min": 10.73,
                            "value": 10.73,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgCO2eq",
                        "use": {"max": 7079.0, "min": 180.9, "value": 3000.0},
                    },
                    "pe": {
                        "description": "Consumption of primary energy",
                        "embedded": {
                            "max": 169.1,
                            "min": 169.1,
                            "value": 169.1,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "MJ",
                        "use": {"max": 3682000.0, "min": 102.2, "value": 100000.0},
                    },
                },
                "manufacturer": {
                    "max": "AMD",
                    "min": "AMD",
                    "source": "Completed from name name based on "
                    "https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=224728652.",
                    "status": "COMPLETED",
                    "value": "AMD",
                },
                "model_range": {
                    "max": "EPYC",
                    "min": "EPYC",
                    "source": "Completed from name name based on "
                    "https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=224728652.",
                    "status": "COMPLETED",
                    "value": "EPYC",
                },
                "name": {
                    "max": "AMD EPYC 7571",
                    "min": "AMD EPYC 7571",
                    "source": "fuzzy match",
                    "status": "COMPLETED",
                    "value": "AMD EPYC 7571",
                },
                "params": {
                    "source": "From TDP",
                    "status": "COMPLETED",
                    "value": {
                        "a": 101.6958680014875,
                        "b": 0.06466257889658457,
                        "c": 20.451103146337097,
                        "d": -4.569671341827919,
                    },
                },
                "pe_factor": {
                    "max": 468.15,
                    "min": 0.013,
                    "source": "ADPf / (1-%renewable_energy)",
                    "status": "DEFAULT",
                    "unit": "MJ/kWh",
                    "value": 12.874,
                },
                "tdp": {
                    "max": 200,
                    "min": 200,
                    "source": "Completed from name name based on "
                    "https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=224728652.",
                    "status": "COMPLETED",
                    "unit": "W",
                    "value": 200,
                },
                "threads": {
                    "max": 64,
                    "min": 64,
                    "source": "Completed from name name based on "
                    "https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=224728652.",
                    "status": "COMPLETED",
                    "value": 64,
                },
                "time_workload": {
                    "max": 100.0,
                    "min": 0.0,
                    "status": "ARCHETYPE",
                    "unit": "%",
                    "value": 50.0,
                },
                "units": {"max": 2.0, "min": 2.0, "status": "ARCHETYPE", "value": 2.0},
                "usage_location": {
                    "status": "DEFAULT",
                    "unit": "CodSP3 - NCS Country Codes " "- NATO",
                    "value": "EEE",
                },
                "use_time_ratio": {
                    "max": 1.0,
                    "min": 1.0,
                    "status": "ARCHETYPE",
                    "unit": "/1",
                    "value": 1.0,
                },
                "workloads": {
                    "status": "COMPLETED",
                    "unit": "workload_rate:W",
                    "value": [
                        {"load_percentage": 0, "power_watt": 24.0},
                        {"load_percentage": 10, "power_watt": 64.0},
                        {"load_percentage": 50, "power_watt": 150.0},
                        {"load_percentage": 100, "power_watt": 204.0},
                    ],
                },
            },
            "MOTHERBOARD-1": {
                "duration": {"unit": "hours", "value": 35040.0},
                "impacts": {
                    "adp": {
                        "description": "Use of minerals and fossil ressources",
                        "embedded": {
                            "max": 0.001384,
                            "min": 0.001384,
                            "value": 0.001384,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgSbeq",
                        "use": "not implemented",
                    },
                    "gwp": {
                        "description": "Total climate change",
                        "embedded": {
                            "max": 24.79,
                            "min": 24.79,
                            "value": 24.79,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgCO2eq",
                        "use": "not implemented",
                    },
                    "pe": {
                        "description": "Consumption of primary energy",
                        "embedded": {
                            "max": 313.5,
                            "min": 313.5,
                            "value": 313.5,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "MJ",
                        "use": "not implemented",
                    },
                },
                "units": {"max": 1, "min": 1, "status": "ARCHETYPE", "value": 1},
            },
            "POWER_SUPPLY-1": {
                "duration": {"unit": "hours", "value": 35040.0},
                "impacts": {
                    "adp": {
                        "description": "Use of minerals and fossil ressources",
                        "embedded": {
                            "max": 0.03112,
                            "min": 0.006225,
                            "value": 0.019,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgSbeq",
                        "use": "not implemented",
                    },
                    "gwp": {
                        "description": "Total climate change",
                        "embedded": {
                            "max": 91.13,
                            "min": 18.23,
                            "value": 54.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgCO2eq",
                        "use": "not implemented",
                    },
                    "pe": {
                        "description": "Consumption of primary energy",
                        "embedded": {
                            "max": 1320.0,
                            "min": 264.0,
                            "value": 800.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "MJ",
                        "use": "not implemented",
                    },
                },
                "unit_weight": {
                    "max": 5.0,
                    "min": 1.0,
                    "status": "ARCHETYPE",
                    "unit": "kg",
                    "value": 2.99,
                },
                "units": {"max": 2.0, "min": 2.0, "status": "ARCHETYPE", "value": 2.0},
            },
            "RAM-1": {
                "adp_factor": {
                    "max": 2.656e-07,
                    "min": 1.32e-08,
                    "source": "ADEME Base IMPACTS ®",
                    "status": "DEFAULT",
                    "unit": "kg Sbeq/kWh",
                    "value": 6.42e-08,
                },
                "avg_power": {
                    "max": 109.05599999999998,
                    "min": 109.05599999999998,
                    "status": "COMPLETED",
                    "unit": "W",
                    "value": 109.05599999999998,
                },
                "capacity": {
                    "max": 32.0,
                    "min": 32.0,
                    "status": "ARCHETYPE",
                    "unit": "GB",
                    "value": 32.0,
                },
                "density": {
                    "max": 2.375,
                    "min": 0.625,
                    "source": "Average of 11 rows",
                    "status": "COMPLETED",
                    "unit": "GB/cm2",
                    "value": 1.2443636363636363,
                },
                "duration": {"unit": "hours", "value": 35040.0},
                "gwp_factor": {
                    "max": 0.9,
                    "min": 0.023,
                    "source": "https://www.sciencedirect.com/science/article/pii/S0306261921012149: \n"
                    "Average of 27 european countries",
                    "status": "DEFAULT",
                    "unit": "kg CO2eq/kWh",
                    "value": 0.38,
                },
                "hours_life_time": {
                    "max": 35040.0,
                    "min": 35040.0,
                    "source": "from device",
                    "status": "COMPLETED",
                    "unit": "hours",
                    "value": 35040.0,
                },
                "impacts": {
                    "adp": {
                        "description": "Use of minerals and " "fossil ressources",
                        "embedded": {
                            "max": 0.05899,
                            "min": 0.03047,
                            "value": 0.04,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgSbeq",
                        "use": {"max": 0.02436, "min": 0.001211, "value": 0.006},
                    },
                    "gwp": {
                        "description": "Total climate change",
                        "embedded": {
                            "max": 1414.0,
                            "min": 418.3,
                            "value": 740.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgCO2eq",
                        "use": {"max": 82540.0, "min": 2109.0, "value": 35000.0},
                    },
                    "pe": {
                        "description": "Consumption of primary energy",
                        "embedded": {
                            "max": 17660.0,
                            "min": 5302.0,
                            "value": 9000.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "MJ",
                        "use": {"max": 42930000.0, "min": 1192.0, "value": 1000000.0},
                    },
                },
                "params": {
                    "source": "(ram_electrical_factor_per_go : 0.284) * (ram_capacity: 32.0) ",
                    "status": "COMPLETED",
                    "value": {"a": 9.088},
                },
                "pe_factor": {
                    "max": 468.15,
                    "min": 0.013,
                    "source": "ADPf / (1-%renewable_energy)",
                    "status": "DEFAULT",
                    "unit": "MJ/kWh",
                    "value": 12.874,
                },
                "time_workload": {
                    "max": 100.0,
                    "min": 0.0,
                    "status": "ARCHETYPE",
                    "unit": "%",
                    "value": 50.0,
                },
                "units": {
                    "max": 24.0,
                    "min": 24.0,
                    "status": "ARCHETYPE",
                    "value": 24.0,
                },
                "usage_location": {
                    "status": "DEFAULT",
                    "unit": "CodSP3 - NCS Country Codes " "- NATO",
                    "value": "EEE",
                },
                "use_time_ratio": {
                    "max": 1.0,
                    "min": 1.0,
                    "status": "ARCHETYPE",
                    "unit": "/1",
                    "value": 1.0,
                },
            },
            "SSD-1": {
                "capacity": {
                    "max": 900.0,
                    "min": 900.0,
                    "status": "ARCHETYPE",
                    "unit": "GB",
                    "value": 900.0,
                },
                "density": {
                    "max": 53.6,
                    "min": 48.5,
                    "source": "Average of 3 rows",
                    "status": "COMPLETED",
                    "unit": "GB/cm2",
                    "value": 50.56666666666666,
                },
                "duration": {"unit": "hours", "value": 35040.0},
                "impacts": {
                    "adp": {
                        "description": "Use of minerals and " "fossil ressources",
                        "embedded": {
                            "max": 0.003464,
                            "min": 0.003242,
                            "value": 0.00337,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgSbeq",
                        "use": "not implemented",
                    },
                    "gwp": {
                        "description": "Total climate " "change",
                        "embedded": {
                            "max": 94.33,
                            "min": 86.56,
                            "value": 91.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "kgCO2eq",
                        "use": "not implemented",
                    },
                    "pe": {
                        "description": "Consumption of " "primary energy",
                        "embedded": {
                            "max": 1167.0,
                            "min": 1071.0,
                            "value": 1126.0,
                            "warnings": [
                                "End of life is not included in the calculation"
                            ],
                        },
                        "unit": "MJ",
                        "use": "not implemented",
                    },
                },
                "units": {"max": 4.0, "min": 4.0, "status": "ARCHETYPE", "value": 4.0},
            },
            "adp_factor": {
                "max": 2.656e-07,
                "min": 1.32e-08,
                "source": "ADEME Base IMPACTS ®",
                "status": "DEFAULT",
                "unit": "kg Sbeq/kWh",
                "value": 6.42e-08,
            },
            "avg_power": {
                "max": 354.0576,
                "min": 265.54319999999996,
                "status": "COMPLETED",
                "unit": "W",
                "value": 294.31037999999995,
            },
            "duration": {"unit": "hours", "value": 35040.0},
            "gwp_factor": {
                "max": 0.9,
                "min": 0.023,
                "source": "https://www.sciencedirect.com/science/article/pii/S0306261921012149: \n"
                "Average of 27 european countries",
                "status": "DEFAULT",
                "unit": "kg CO2eq/kWh",
                "value": 0.38,
            },
            "hours_life_time": {
                "max": 35040.0,
                "min": 35040.0,
                "source": "from device",
                "status": "COMPLETED",
                "unit": "hours",
                "value": 35040.0,
            },
            "memory": {"status": "ARCHETYPE", "unit": "GB", "value": 384.0},
            "other_consumption_ratio": {
                "max": 0.6,
                "min": 0.2,
                "status": "ARCHETYPE",
                "unit": "ratio /1",
                "value": 0.33,
            },
            "pe_factor": {
                "max": 468.15,
                "min": 0.013,
                "source": "ADPf / (1-%renewable_energy)",
                "status": "DEFAULT",
                "unit": "MJ/kWh",
                "value": 12.874,
            },
            "ssd_storage": {"status": "ARCHETYPE", "unit": "GB", "value": 1800.0},
            "units": {"max": 1, "min": 1, "status": "ARCHETYPE", "value": 1},
            "usage_location": {
                "status": "DEFAULT",
                "unit": "CodSP3 - NCS Country Codes - NATO",
                "value": "EEE",
            },
            "use_time_ratio": {
                "max": 1.0,
                "min": 1.0,
                "status": "ARCHETYPE",
                "unit": "/1",
                "value": 1.0,
            },
            "vcpu": {"status": "ARCHETYPE", "value": 48.0},
        },
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_empty_usage_eadsv5_type1():
    test = CloudPlatformTest(
        CloudPlatformRequest("azure", "Eadsv5-Type1"),
        ADPImpact(
            ImpactOutput(0.2998, 0.1683, 0.22, END_OF_LIFE_WARNING),
            ImpactOutput(0.01242, 0.0004628, 0.002),
        ),
        GWPImpact(
            ImpactOutput(3648.0, 1380.0, 2200.0, END_OF_LIFE_WARNING),
            ImpactOutput(42070.0, 806.4, 15000.0),
        ),
        PEImpact(
            ImpactOutput(46610.0, 17890.0, 28000.0, END_OF_LIFE_WARNING),
            ImpactOutput(21880000.0, 455.8, 1000000.0),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_usage_with_complex_time_workload_eadsv5_type1():
    test = CloudPlatformTest(
        CloudPlatformRequest(
            "azure",
            "Eadsv5-Type1",
            usage={
                "time_workload": [
                    {"time_percentage": 50, "load_percentage": 0},
                    {"time_percentage": 25, "load_percentage": 60},
                    {"time_percentage": 25, "load_percentage": 100},
                ]
            },
        ),
        ADPImpact(
            ImpactOutput(0.2998, 0.1683, 0.22, END_OF_LIFE_WARNING),
            ImpactOutput(0.01055, 0.0003933, 0.002),
        ),
        GWPImpact(
            ImpactOutput(3648.0, 1380.0, 2200.0, END_OF_LIFE_WARNING),
            ImpactOutput(35750.0, 685.3, 13000.0),
        ),
        PEImpact(
            ImpactOutput(46610.0, 17890.0, 28000.0, END_OF_LIFE_WARNING),
            ImpactOutput(18600000.0, 387.3, 400000.0, UNCERTAINTY_WARNING),
        ),
    )

    await test.check_result()


@pytest.mark.asyncio
async def test_empty_usage_scw_dev1():
    test = CloudPlatformTest(
        CloudPlatformRequest("scaleway", "scw_dev1.base"),
        ADPImpact(
            ImpactOutput(0.1002, 0.07315, 0.08, END_OF_LIFE_WARNING),
            ImpactOutput(0.005804, 0.0002163, 0.0012),
        ),
        GWPImpact(
            ImpactOutput(1432.0, 682.9, 970.0, END_OF_LIFE_WARNING),
            ImpactOutput(19670.0, 377.0, 7000.0),
        ),
        PEImpact(
            ImpactOutput(18210.0, 8736.0, 12500.0, END_OF_LIFE_WARNING),
            ImpactOutput(10230000.0, 213.1, 200000.0, UNCERTAINTY_WARNING),
        ),
    )

    await test.check_result()

