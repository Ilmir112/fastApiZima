import pytest
from httpx import AsyncClient

from zimaApp.wells_data.dao import WellsDatasDAO
from datetime import datetime

from zimaApp.wells_data.schemas import SWellsData


@pytest.mark.parametrize(
    "well_number,area_well,well_oilfield,cdng,costumer,inventory_number,wellhead_fittings,appointment,angle_data,"
    "column_direction,column_conductor,column_production,column_additional,bottom_hole_drill,bottom_hole_artificial,"
    "max_angle,distance_from_rotor_table,max_angle_depth,max_expected_pressure,max_admissible_pressure,"
    "rotor_altitude,perforation,equipment,nkt_data,sucker_pod,diameter_doloto_ek,last_pressure_date,"
    "date_commissioning,date_drilling_run,date_drilling_finish,geolog,date_create,status_code",
    [(
      "1225",
      "Туймазинская",
      "Туймазинское",
      "БНЛ",
      "ТЦНГ 01",
      "12356",
      "АУШГН-146",
      "нефтяная",
      {
          "additionalProp1": {}
      },
      {
          "diameter": 299,
          "wall_thickness": 7,
          "head": 0,
          "shoe": 300,
          "level_cement": 0
      },
      {
          "diameter": 210,
          "wall_thickness": 10,
          "head": 0,
          "shoe": 500,
          "level_cement": 0
      },
      {
          "diameter": 146,
          "wall_thickness": 7.7,
          "head": 0,
          "shoe": 1500,
          "level_cement": 300
      },
      {
          "diameter": 114,
          "wall_thickness": 7,
          "head": 1000,
          "shoe": 1600,
          "level_cement": 1000
      },
      150.5,
      1500,
      float(25),
      3.6,
      float(1000),
      float(100),
      float(100),
      3.6,
      {
          "спец.\nотверстия": {
              "вертикаль": [1140.79],
              "отрайбировано": False,
              "Прошаблонировано": False,
              "интервал": [[1257.0, 1258.0]],
              "вскрытие": ["2025-05-04"],
              "отключение": True,
              "давление": [0, 0, 0],
              "замер": [0],
              "рабочая жидкость": [0.01, 1.01, 1.01],
              "БСУ": 89,
              "кровля": 1257.0,
              "подошва": 1258.0
          },
          "C1rd-bb": {
              "вертикаль": [1125.3, 1125.3, 1128.84, 1128.84],
              "отрайбировано": False,
              "Прошаблонировано": False,
              "интервал": [
                  [1241.2, 1243.6],
                  [1244.8, 1246.8]
              ],
              "вскрытие": [
                  "2025-05-04",
                  "2025-05-04",
                  "2025-05-04",
                  "2025-05-04"
              ],
              "отключение": False,
              "давление": [120.9, 0, 0],
              "замер": ["2025-04-25", 0, 0, 0],
              "рабочая жидкость": [1.21, 0.01, 0.01, 0.01, 1.2, 1.2],
              "БСУ": 106,
              "кровля": 1241.2,
              "подошва": 1246.8
          }
      },
      {"before": "0", "after": "0"},
      {"before": "0", "after": "0"},
      {"before": "0", "after": "0"},
      25.0,
      "2025-05-04",
      "2025-05-04",
      "2025-05-04",
      "2025-05-04",
      "Ilmir112",
      "2025-05-04", 200
      )
     ]
)
async def test_add_wells_data(
        well_number,
        area_well,
        well_oilfield,
        cdng,
        costumer,
        inventory_number,
        wellhead_fittings,
        appointment,
        angle_data,
        column_direction,
        column_conductor,
        column_production,
        column_additional,
        bottom_hole_drill,
        bottom_hole_artificial,
        max_angle,
        distance_from_rotor_table,
        max_angle_depth,
        max_expected_pressure,
        max_admissible_pressure,
        rotor_altitude,
        perforation,
        equipment,
        nkt_data,
        sucker_pod,
        diameter_doloto_ek,
        last_pressure_date,
        date_commissioning,
        date_drilling_run,
        date_drilling_finish,
        geolog,
        date_create,
        status_code,
        ac: AsyncClient,
):
    response = await ac.post(
        "/wells_data_router/add_wells_data",
        json={"well_number": well_number,
              "area_well": area_well,
              "well_oilfield": well_oilfield,
              "cdng": cdng,
              "costumer": costumer,
              "inventory_number": inventory_number,
              "wellhead_fittings": wellhead_fittings,
              "appointment": appointment,
              "angle_data": angle_data,
              "column_direction": column_direction,
              "column_conductor": column_conductor,
              "column_production": column_production,
              "column_additional": column_additional,
              "bottom_hole_drill": bottom_hole_drill,
              "bottom_hole_artificial": bottom_hole_artificial,
              "max_angle": max_angle,
              "distance_from_rotor_table": distance_from_rotor_table,
              "max_angle_depth": max_angle_depth,
              "max_expected_pressure": max_expected_pressure,
              "max_admissible_pressure": max_admissible_pressure,
              "rotor_altitude": rotor_altitude,
              "perforation": perforation,
              "equipment": equipment,
              "nkt_data": nkt_data,
              "sucker_pod": sucker_pod,
              "diameter_doloto_ek": diameter_doloto_ek,
              "last_pressure_date": last_pressure_date,
              "date_commissioning": date_commissioning,
              "date_drilling_run": date_drilling_run,
              "date_drilling_finish": date_drilling_finish,
              "geolog": geolog,
              "date_create": date_create},
    )
    assert response.status_code == status_code

# async def test_add_wells_data(well_data: SWellsData):
#     wells = await WellsDatasDAO.add_data(
#         well_number=well_data.well_number,
#         area_well=well_data.area_well,
#         well_oilfield=well_data.well_oilfield,
#         cdng=well_data.cdng,
#         costumer=well_data.costumer,
#         inventory_number=well_data.inventory_number,
#         wellhead_fittings=well_data.wellhead_fittings,
#         appointment=well_data.appointment,
#         angle_data=well_data.angle_data,
#         column_direction=well_data.column_direction,
#         column_conductor=well_data.column_conductor,
#         column_production=well_data.column_production,
#         column_additional=well_data.column_additional,
#         bottom_hole_drill=well_data.bottom_hole_drill,
#         bottom_hole_artificial=well_data.bottom_hole_artificial,
#         max_angle=well_data.max_angle,
#         distance_from_rotor_table=well_data.distance_from_rotor_table,
#         max_angle_depth=well_data.max_angle_depth,
#         max_expected_pressure=well_data.max_expected_pressure,
#         max_admissible_pressure=well_data.max_admissible_pressure,
#         rotor_altitude=well_data.rotor_altitude,
#         perforation=well_data.perforation,
#         equipment=well_data.equipment,
#         nkt_data=well_data.nkt_data,
#         sucker_pod=well_data.sucker_pod,
#         diameter_doloto_ek=well_data.diameter_doloto_ek,
#         last_pressure_date=well_data.last_pressure_date,
#         date_commissioning=well_data.date_commissioning,
#         date_drilling_run=well_data.date_drilling_run,
#         date_drilling_finish=well_data.date_drilling_finish,
#         geolog=well_data.geolog,
#         date_create=well_data.date_create
#     )
#
#     # Проверка, что запись успешно добавлена
#     assert wells is not None
#     assert wells.well_number == "1225"
