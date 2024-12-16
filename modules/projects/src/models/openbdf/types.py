import logging
from datetime import date, datetime
from typing import Union
from uuid import UUID

import strawberry
from iso3166 import countries
from lcax import AreaType as LCAxAreaType
from lcax import Assembly as LCAxAssembly
from lcax import BuildingInfo as LCAxProjectInfo
from lcax import Classification as LCAxClassification
from lcax import Conversion as LCAxConversion
from lcax import EPD as LCAxEPD
from lcax import Location as LCAxLocation
from lcax import Product as LCAxProduct
from lcax import Project as LCAxProject
from lcax import SoftwareInfo as LCAxSoftwareInfo
from lcax import Source as LCAxSource
from lcax import TechFlow as LCAxTechFlow
from lcax import ValueUnit as LCAxValueUnit
from strawberry.scalars import JSON, Base64

from models.openbdf.enums import (
    GraphQLUnit,
    GraphQLCountry,
    GraphQLStandard,
    GraphQLSubType,
    GraphQLBuildingType,
    GraphQLBuildingTypology,
    GraphQLGeneralEnergyClass,
    GraphQLRoofType,
    GraphQLImpactCategoryKey,
    GraphQLLifeCycleStage,
    GraphQLProjectPhase,
    GraphQLBuildingModelScope,
)
from models.openbdf.utils import _resolve_dict_value

logger = logging.getLogger("main")


@strawberry.experimental.pydantic.type(model=LCAxValueUnit, name="ValueUnit")
class GraphQLValueUnit:
    unit: GraphQLUnit
    value: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxAreaType, name="AreaType")
class GraphQLAreaType:
    unit: GraphQLUnit
    value: strawberry.auto
    definition: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxConversion, name="Conversion")
class GraphQLConversion:
    meta_data: strawberry.auto
    to: GraphQLUnit
    value: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxSource, name="Source", all_fields=True)
class GraphQLSource:
    pass


@strawberry.type(name="ImpactCategoryResults")
class GraphQLImpactCategoryResults:
    @strawberry.field()
    def a0(self: dict) -> float | None:
        return self.get("a0")

    @strawberry.field()
    def a1a3(self: dict) -> float | None:
        return self.get("a1a3")

    @strawberry.field()
    def a4(self: dict) -> float | None:
        return self.get("a4")

    @strawberry.field()
    def a5(self: dict) -> float | None:
        return self.get("a5")

    @strawberry.field()
    def b1(self: dict) -> float | None:
        return self.get("b1")

    @strawberry.field()
    def b2(self: dict) -> float | None:
        return self.get("b2")

    @strawberry.field()
    def b3(self: dict) -> float | None:
        return self.get("b3")

    @strawberry.field()
    def b4(self: dict) -> float | None:
        return self.get("b4")

    @strawberry.field()
    def b5(self: dict) -> float | None:
        return self.get("b5")

    @strawberry.field()
    def b6(self: dict) -> float | None:
        return self.get("b6")

    @strawberry.field()
    def b7(self: dict) -> float | None:
        return self.get("b7")

    @strawberry.field()
    def b8(self: dict) -> float | None:
        return self.get("b8")

    @strawberry.field()
    def c1(self: dict) -> float | None:
        return self.get("c1")

    @strawberry.field()
    def c2(self: dict) -> float | None:
        return self.get("c2")

    @strawberry.field()
    def c3(self: dict) -> float | None:
        return self.get("c3")

    @strawberry.field()
    def c4(self: dict) -> float | None:
        return self.get("c4")

    @strawberry.field()
    def d(self: dict) -> float | None:
        return self.get("d")

    @strawberry.field()
    def total(self: dict) -> float | None:
        total = 0
        for value in self.values():
            if isinstance(value, float):
                total += value
        return total


@strawberry.type(name="Results")
class GraphQLResults:
    @strawberry.field()
    def gwp(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("gwp")

    @strawberry.field()
    def gwp_fos(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("gwp_fos")

    @strawberry.field()
    def gwp_bio(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("gwp_bio")

    @strawberry.field()
    def gwp_lul(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("gwp_lul")

    @strawberry.field()
    def odp(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("odp")

    @strawberry.field()
    def ap(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("ap")

    @strawberry.field()
    def ep(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("ep")

    @strawberry.field()
    def ep_fw(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("ep_fw")

    @strawberry.field()
    def ep_mar(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("ep_mar")

    @strawberry.field()
    def ep_ter(self) -> GraphQLImpactCategoryResults | None:
        return self.get("ep_ter")

    @strawberry.field()
    def pocp(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("pocp")

    @strawberry.field()
    def adpe(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("adpe")

    @strawberry.field()
    def adpf(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("adpf")

    @strawberry.field()
    def penre(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("penre")

    @strawberry.field()
    def pere(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("pere")

    @strawberry.field()
    def perm(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("perm")

    @strawberry.field()
    def pert(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("pert")

    @strawberry.field()
    def penrt(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("penrt")

    @strawberry.field()
    def penrm(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("penrm")

    @strawberry.field()
    def sm(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("sm")

    @strawberry.field()
    def pm(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("pm")

    @strawberry.field()
    def wdp(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("wdp")

    @strawberry.field()
    def irp(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("irp")

    @strawberry.field()
    def etp_fw(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("etp_fw")

    @strawberry.field()
    def htp_c(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("htp_c")

    @strawberry.field()
    def htp_nc(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("htp_nc")

    @strawberry.field()
    def sqp(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("sqp")

    @strawberry.field()
    def rsf(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("rsf")

    @strawberry.field()
    def nrsf(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("nrsf")

    @strawberry.field()
    def fw(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("fw")

    @strawberry.field()
    def hwd(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("hwd")

    @strawberry.field()
    def nhwd(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("nhwd")

    @strawberry.field()
    def rwd(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("rwd")

    @strawberry.field()
    def cru(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("cru")

    @strawberry.field()
    def mrf(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("mrf")

    @strawberry.field()
    def mer(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("mer")

    @strawberry.field()
    def eee(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("eee")

    @strawberry.field()
    def eet(self: dict) -> GraphQLImpactCategoryResults | None:
        return self.get("eet")


@strawberry.experimental.pydantic.type(model=LCAxEPD, name="EPD")
class GraphQLEPD:
    comment: strawberry.auto
    conversions: list[GraphQLConversion] | None = None
    declared_unit: GraphQLUnit
    format_version: strawberry.auto
    id: UUID
    impacts: GraphQLResults
    location: GraphQLCountry
    meta_data: JSON
    name: strawberry.auto
    published_date: strawberry.auto
    reference_service_life: strawberry.auto
    source: GraphQLSource | None = None
    standard: GraphQLStandard
    subtype: GraphQLSubType
    valid_until: strawberry.auto
    version: strawberry.auto


@strawberry.experimental.pydantic.type(model=LCAxTechFlow, name="TechFlow")
class GraphQLTechFlow:
    comment: strawberry.auto
    conversions: list[GraphQLConversion] | None = None
    declared_unit: GraphQLUnit
    format_version: strawberry.auto
    id: UUID
    impacts: GraphQLResults
    location: GraphQLCountry
    meta_data: JSON
    name: strawberry.auto
    source: GraphQLSource | None = None


@strawberry.type(name="ProductMetaData")
class GraphQLProductMetaData:
    product_class: str | None = None
    strength: GraphQLValueUnit | None = None
    density: GraphQLValueUnit | None = None
    exposure_classes: str | None = None
    concrete_precast: str | None = None
    brick_type: str | None = None
    brick_grout_included: bool | None = None
    timber_type: str | None = None
    grout_type: str | None = None


@strawberry.experimental.pydantic.type(model=LCAxProduct, name="Product")
class GraphQLProduct:
    description: strawberry.auto
    id: UUID
    impact_data: Union[GraphQLEPD, GraphQLTechFlow]
    meta_data: GraphQLProductMetaData | None = None
    name: strawberry.auto
    quantity: strawberry.auto
    reference_service_life: int
    results: GraphQLResults | None = None
    unit: GraphQLUnit


@strawberry.experimental.pydantic.type(model=LCAxClassification, name="Classification", all_fields=True)
class GraphQLClassification:
    pass


@strawberry.type(name="AssemblyMetaData")
class GraphQLAssemblyMetaData:
    volume: GraphQLValueUnit | None = None


@strawberry.experimental.pydantic.type(model=LCAxAssembly, name="Assembly")
class GraphQLAssembly:
    classification: list[GraphQLClassification] | None = None
    comment: strawberry.auto
    description: strawberry.auto
    id: UUID
    meta_data: GraphQLAssemblyMetaData | None = None
    name: strawberry.auto
    products: list[GraphQLProduct]
    quantity: strawberry.auto
    results: GraphQLResults | None = None
    unit: GraphQLUnit


@strawberry.experimental.pydantic.type(model=LCAxLocation, name="Location")
class GraphQLLocation:
    address: strawberry.auto
    city: strawberry.auto
    country: GraphQLCountry

    @strawberry.field
    def country_name(self) -> str:
        try:
            return countries.get(self.country.value).name
        except KeyError:
            return self.country.value

    @strawberry.field
    async def longitude(self) -> float:
        from models.database.methods import get_coordinates

        location = await get_coordinates(self.country.value)
        return location.get("longitude", 0.0)

    @strawberry.field
    async def latitude(self) -> float:
        from models.database.methods import get_coordinates

        location = await get_coordinates(self.country.value)
        return location.get("latitude", 0.0)


@strawberry.experimental.pydantic.type(model=LCAxProjectInfo, name="ProjectInfo")
class GraphQLProjectInfo:
    building_completion_year: strawberry.auto
    building_footprint: GraphQLValueUnit | None = None
    building_height: GraphQLValueUnit | None = None
    building_mass: GraphQLValueUnit | None = None
    building_model_scope: list[GraphQLBuildingModelScope] | None = None
    building_permit_year: strawberry.auto
    building_type: GraphQLBuildingType
    building_typology: list[GraphQLBuildingTypology]
    building_users: strawberry.auto
    certifications: strawberry.auto
    energy_demand_electricity: strawberry.auto
    energy_demand_heating: strawberry.auto
    energy_supply_electricity: strawberry.auto
    energy_supply_heating: strawberry.auto
    exported_electricity: strawberry.auto
    floors_above_ground: strawberry.auto
    floors_below_ground: strawberry.auto
    frame_type: strawberry.auto
    general_energy_class: GraphQLGeneralEnergyClass
    gross_floor_area: GraphQLAreaType | None = None
    heated_floor_area: GraphQLAreaType | None = None
    local_energy_class: strawberry.auto
    roof_type: GraphQLRoofType


@strawberry.experimental.pydantic.type(model=LCAxSoftwareInfo, name="SoftwareInfo", all_fields=True)
class GraphQLSoftwareInfo:
    pass


@strawberry.type(name="Assessor")
class GraphQLAssessor:
    @strawberry.field
    def name(self: dict) -> str | None:
        return self.get("name")

    @strawberry.field
    def email(self: dict) -> str | None:
        return self.get("email")

    @strawberry.field
    def organization(self: dict) -> str | None:
        return self.get("organization")


@strawberry.type(name="AssessmentMetaData")
class GraphQLAssessmentMetaData:
    assessment_methodology_description: str | None = None
    uncertainty: float | None = None
    cutoff_method: str | None = None
    assessor: GraphQLAssessor | None = None
    year: int | None = None

    @strawberry.field
    def date(self) -> date | None:
        value = self.date
        if not value:
            return None
        elif isinstance(value, str):
            return datetime.strptime(value, "%d/%m/%Y %H:%M:%S").date()
        else:
            return value

    quantity_source: str | None = None
    quantity_source_detail: str | None = None
    purpose: str | None = None
    iso21931_compliance: bool | None = None
    en15978_compliance: bool | None = None
    rics_2017_compliance: bool | None = None
    rics_2023_compliance: bool | None = None
    ashrae_240p_compliance: bool | None = None
    sei_prestandard_compliance: bool | None = None
    verified: bool | None = None
    verified_info: str | None = None
    validity_period: str | None = None
    results_validation_description: str | None = None
    tool_report_upload: Base64 | None = None
    report_name: str | None = None
    additional_lca_report_name: str | None = None
    project_phase_at_reporting: str | None = None
    project_phase_at_time_of_assessment: str | None = None
    operational_energy_included: bool | None = None
    biogenic_carbon_included: bool | None = None
    biogenic_carbon_accounting_method: str | None = None
    bio_sustainability_certification: str | None = None
    biogenic_carbon_description: str | None = None
    project_refrigerants: str | None = None
    refrigerant_type_included: str | None = None
    substructure_scope: str | None = None
    shell_superstructure_scope: str | None = None
    shell_exterior_enclosure_scope: str | None = None
    interior_construction_scope: str | None = None
    interior_finishes_scope: str | None = None
    services_mechanical_scope: str | None = None
    services_electrical_scope: str | None = None
    services_plumbing_scope: str | None = None
    sitework_scope: str | None = None
    equipment_scope: str | None = None
    furnishings_scope: str | None = None
    lca_requirements: str | None = None


@strawberry.type(name="Owner")
class GraphQLOwnerMetaData:
    @strawberry.field
    def contact(self: dict) -> str | None:
        return self.get("contact")

    @strawberry.field
    def web(self: dict) -> str | None:
        return self.get("web")

    @strawberry.field
    def country(self: dict) -> str | None:
        return self.get("country")

    @strawberry.field
    def email(self: dict) -> str | None:
        return self.get("email")

    @strawberry.field
    def type(self: dict) -> str | None:
        return self.get("type")

    @strawberry.field
    def representative(self: dict) -> str | None:
        return self.get("representative")


@strawberry.type(name="Energy")
class GraphQLEnergyMetaData:
    @strawberry.field
    def tool_energy_modeling(self: dict) -> str | None:
        return self.get("tool_energy_modeling")

    @strawberry.field
    def tool_energy_modeling_version(self: dict) -> str | None:
        return self.get("tool_energy_modeling_version")

    @strawberry.field
    def energy_model_methodology_reference(self: dict) -> str | None:
        return self.get("energy_model_methodology_reference")

    @strawberry.field
    def gwp_energy_sources_year(self: dict) -> float | None:
        return self.get("gwp_energy_sources_year")

    @strawberry.field
    def site_location_weather_data(self: dict) -> str | None:
        return self.get("site_location_weather_data")

    @strawberry.field
    def electricity_provider(self: dict) -> str | None:
        return self.get("electricity_provider")

    @strawberry.field
    def electricity_source(self: dict) -> str | None:
        return self.get("electricity_source")

    @strawberry.field
    def electricity_carbon_factor(self: dict) -> float | None:
        return self.get("electricity_carbon_factor")

    @strawberry.field
    def electricity_carbon_factor_source(self: dict) -> str | None:
        return self.get("electricity_carbon_factor_source")


@strawberry.type(name="Cost")
class GraphQLCostMetaData:
    currency: str | None = None
    total_cost: float | None = None
    hard_cost: float | None = None
    soft_cost: float | None = None
    siteworks_cost: float | None = None
    cost_source: str | None = None
    notes: str | None = None


@strawberry.type(name="Publication")
class GraphQLPublicationMetaData:
    @strawberry.field
    def authors(self: dict) -> str | None:
        return self.get("authors")

    @strawberry.field
    def year(self: dict) -> int | None:
        return self.get("year")

    @strawberry.field
    def doi(self: dict) -> str | None:
        return self.get("doi")

    @strawberry.field
    def title(self: dict) -> str | None:
        return self.get("title")

    @strawberry.field
    def publisher(self: dict) -> str | None:
        return self.get("publisher")


@strawberry.type(name="Structural")
class GraphQLStructuralMetaData:
    @strawberry.field
    def column_grid_long(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "column_grid_long", GraphQLValueUnit)

    risk_category: str | None = None

    @strawberry.field
    def live_load(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "live_load", GraphQLValueUnit)

    @strawberry.field
    def snow_load(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "snow_load", GraphQLValueUnit)

    @strawberry.field
    def wind_speed(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "wind_speed", GraphQLValueUnit)

    earthquake_importance_factor: float | None = None
    seismic_design_category: str | None = None
    horizontal_gravity_system: str | None = None
    secondary_horizontal_gravity_system: str | None = None
    vertical_gravity_system: str | None = None
    secondary_vertical_gravity_system: str | None = None
    lateral_system: str | None = None
    podium: str | None = None

    @strawberry.field
    def allowable_soil_bearing_pressure(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "allowable_soil_bearing_pressure", GraphQLValueUnit)

    foundation_type: str | None = None


@strawberry.type(name="ProjectMetaData")
class GraphQLProjectMetaData:
    @strawberry.field
    def source(self: dict) -> GraphQLSource | None:
        return _resolve_dict_value(self, "source", GraphQLSource)

    @strawberry.field
    def product_classification_system(self: dict) -> str | None:
        return self.get("product_classification_system")

    @strawberry.field
    def image(self: dict) -> Base64 | None:
        return self.get("image")

    @strawberry.field
    def climate_zone(self: dict) -> str | None:
        return self.get("climate_zone")

    @strawberry.field
    def owner(self: dict) -> GraphQLOwnerMetaData | None:
        return _resolve_dict_value(self, "owner", GraphQLOwnerMetaData)

    @strawberry.field
    def assessment(self: dict) -> GraphQLAssessmentMetaData | None:
        return _resolve_dict_value(self, "assessment", GraphQLAssessmentMetaData)

    @strawberry.field
    def lca_software_version(self: dict) -> str | None:
        return self.get("lca_software_version")

    @strawberry.field
    def lca_database(self: dict) -> str | None:
        return self.get("lca_database")

    @strawberry.field()
    def lca_database_version(self: dict) -> str | None:
        return self.get("lca_database_version")

    @strawberry.field
    def lca_database_other(self: dict) -> str | None:
        return self.get("lca_database_other")

    @strawberry.field
    def lca_model_type(self: dict) -> str | None:
        return self.get("lca_model_type")

    @strawberry.field
    def interstitial_floors(self: dict) -> str | None:
        return self.get("interstitial_floors")

    @strawberry.field
    def newly_built_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "newly_built_area", GraphQLValueUnit)

    @strawberry.field
    def retrofitted_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "retrofitted_area", GraphQLValueUnit)

    @strawberry.field
    def demolished_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "demolished_area", GraphQLValueUnit)

    @strawberry.field
    def existing_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "existing_area", GraphQLValueUnit)

    @strawberry.field
    def built_floor_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "built_floor_area", GraphQLValueUnit)

    @strawberry.field
    def building_project_construction_type_2(self: dict) -> str | None:
        return self.get("building_project_construction_type_2")

    @strawberry.field
    def infrastructure_project_construction_type(self: dict) -> str | None:
        return self.get("infrastructure_project_construction_type")

    @strawberry.field
    def infrastructure_sector_type(self: dict) -> str | None:
        return self.get("infrastructure_sector_type")

    @strawberry.field
    def building_use_type(self: dict) -> str | None:
        return self.get("building_use_type")

    @strawberry.field
    def infrastructure_use_type(self: dict) -> str | None:
        return self.get("infrastructure_use_type")

    @strawberry.field
    def project_work_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "project_work_area", GraphQLValueUnit)

    @strawberry.field
    def project_site_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "project_site_area", GraphQLValueUnit)

    @strawberry.field
    def conditioned_floor_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "conditioned_floor_area", GraphQLValueUnit)

    @strawberry.field
    def unconditioned_floor_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "unconditioned_floor_area", GraphQLValueUnit)

    @strawberry.field
    def enclosed_parking_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "enclosed_parking_area", GraphQLValueUnit)

    @strawberry.field
    def detached_parking_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "detached_parking_area", GraphQLValueUnit)

    @strawberry.field
    def surface_parking_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "surface_parking_area", GraphQLValueUnit)

    @strawberry.field
    def detached_parking_structure_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "detached_parking_structure_area", GraphQLValueUnit)

    @strawberry.field
    def ibc_construction_type(self: dict) -> str | None:
        return self.get("ibc_construction_type")

    @strawberry.field
    def project_surroundings(self: dict) -> str | None:
        return self.get("project_surroundings")

    @strawberry.field
    def project_historic(self: dict) -> bool | None:
        return self.get("project_historic")

    @strawberry.field
    def full_time_equivalent(self: dict) -> float | None:
        return self.get("full_time_equivalent")

    @strawberry.field
    def occupant_load(self: dict) -> float | None:
        return self.get("occupant_load")

    @strawberry.field
    def mean_roof_height(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "mean_roof_height", GraphQLValueUnit)

    @strawberry.field
    def window_wall_ratio(self: dict) -> float | None:
        return self.get("window_wall_ratio")

    @strawberry.field
    def thermal_envelope_area(self: dict) -> GraphQLValueUnit | None:
        return _resolve_dict_value(self, "thermal_envelope_area", GraphQLValueUnit)

    @strawberry.field
    def residential_units(self: dict) -> int | None:
        return self.get("residential_units")

    @strawberry.field
    def bedroom_count(self: dict) -> int | None:
        return self.get("bedroom_count")

    @strawberry.field
    def project_expected_life(self: dict) -> int | None:
        return self.get("project_expected_life")

    @strawberry.field
    def results_validated_as_built(self: dict) -> bool | None:
        return self.get("results_validated_as_built")

    @strawberry.field
    def results_validated_as_built_description(self: dict) -> str | None:
        return self.get("results_validated_as_built_description")

    @strawberry.field
    def assessment_cutoff_type(self: dict) -> str | None:
        return self.get("assessment_cutoff_type")

    @strawberry.field
    def assessment_cutoff(self: dict) -> str | None:
        return self.get("assessment_cutoff")

    @strawberry.field
    def assessment_cost_cutoff(self: dict) -> str | None:
        return self.get("assessment_cost_cutoff")

    @strawberry.field
    def heritage_status(self: dict) -> str | None:
        return self.get("heritage_status")

    @strawberry.field
    def omniclass_construction_entity(self: dict) -> str | None:
        return self.get("omniclass_construction_entity")

    @strawberry.field
    def energy(self: dict) -> GraphQLEnergyMetaData | None:
        return _resolve_dict_value(self, "energy", GraphQLEnergyMetaData)

    @strawberry.field
    def architect_of_record(self: dict) -> str | None:
        return self.get("architect_of_record")

    @strawberry.field
    def project_user_studio(self: dict) -> str | None:
        return self.get("project_user_studio")

    @strawberry.field
    def general_contractor(self: dict) -> str | None:
        return self.get("general_contractor")

    @strawberry.field
    def mep_engineer(self: dict) -> str | None:
        return self.get("mep_engineer")

    @strawberry.field
    def sustainability_consultant(self: dict) -> str | None:
        return self.get("sustainability_consultant")

    @strawberry.field
    def structural_engineer(self: dict) -> str | None:
        return self.get("structural_engineer")

    @strawberry.field
    def civil_engineer(self: dict) -> str | None:
        return self.get("civil_engineer")

    @strawberry.field
    def landscape_consultant(self: dict) -> str | None:
        return self.get("landscape_consultant")

    @strawberry.field
    def interior_designer(self: dict) -> str | None:
        return self.get("interior_designer")

    @strawberry.field
    def other_project_team(self: dict) -> str | None:
        return self.get("other_project_team")

    @strawberry.field
    def work_completion_year(self: dict) -> int | None:
        return self.get("work_completion_year")

    @strawberry.field
    def construction_start(self: dict) -> str | None:
        return self.get("construction_start")

    @strawberry.field
    def construction_year_existing_building(self: dict) -> int | None:
        return self.get("construction_year_existing_building")

    @strawberry.field
    def building_occupancy_start(self: dict) -> str | None:
        return self.get("building_occupancy_start")

    @strawberry.field
    def cost(self: dict) -> GraphQLCostMetaData | None:
        return _resolve_dict_value(self, "cost", GraphQLCostMetaData)

    @strawberry.field
    def structural(self: dict) -> GraphQLStructuralMetaData | None:
        return _resolve_dict_value(self, "structural", GraphQLStructuralMetaData)

    @strawberry.field
    def publication(self: dict) -> GraphQLPublicationMetaData | None:
        return _resolve_dict_value(self, "publication", GraphQLPublicationMetaData)


@strawberry.experimental.pydantic.type(model=LCAxProject, name="Project")
class GraphQLProject:
    assemblies: list[GraphQLAssembly]
    classification_system: strawberry.auto
    comment: strawberry.auto
    description: strawberry.auto
    format_version: str = "0.2.0"
    id: UUID
    impact_categories: list[GraphQLImpactCategoryKey]
    lcia_method: strawberry.auto
    life_cycle_stages: list[GraphQLLifeCycleStage]
    location: GraphQLLocation
    meta_data: GraphQLProjectMetaData | None = None
    name: strawberry.auto
    owner: str | None = None
    project_info: GraphQLProjectInfo
    project_phase: GraphQLProjectPhase
    reference_study_period: strawberry.auto
    results: GraphQLResults | None = None
    software_info: GraphQLSoftwareInfo
