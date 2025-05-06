import pytest

from zimaApp.well_classifier.dao import WellClassifierDAO
from datetime import datetime


@pytest.mark.parametrize(
    "well_number,deposit_area",
    [("125", "Туймазинская"), ("125", "Туймазинска"), ("1252", "Туймазинская")],
)
async def test_add_data_well_classifier(well_number, deposit_area):
    wells = WellClassifierDAO.add_data(
        cdng="ТЦДНГ 02",
        well_number="125",
        deposit_area="Туймазинская",
        oilfield="Туймазинское",
        category_pressure="1",
        pressure_ppl="25",
        pressure_gst="34",
        date_measurement="daw",
        category_h2s="2",
        h2s_pr="2",
        h2s_mg_l="21",
        h2s_mg_m="3",
        category_gf="25",
        gas_factor="30",
        today=datetime.strptime("2025-05-04", "%Y-%m-%d"),
        region="ТГМ",
        costumer="БНД",
    )
    # print(wells)
    # assert wells.well_number == "125"
    #
    # # Проверка добавления брони
    # new_booking = await WellClassifierDAO.find_one_or_none(id=wells.id)
    #
    # assert new_booking is not None
    #
    # # Удаление брони
    # await WellClassifierDAO.delete(
    #     id=new_booking["id"],
    #     well_number=wells["well_number"],
    # )
    #
    # # Проверка удаления брони
    # deleted_wells = await WellClassifierDAO.find_one_or_none(id=wells["id"])
    # assert deleted_wells is None
