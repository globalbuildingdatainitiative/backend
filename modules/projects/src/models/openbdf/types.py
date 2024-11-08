from datetime import date
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
    @strawberry.field
    def assessment_methodology_description(self: dict) -> str | None:
        return self.get("assessment_methodology_description")

    @strawberry.field
    def uncertainty(self: dict) -> float | None:
        return self.get("uncertainty")

    @strawberry.field
    def cutoff_method(self: dict) -> str | None:
        return self.get("cutoff_method")

    @strawberry.field
    def assessor(self: dict) -> GraphQLAssessor | None:
        return self.get("assessor")

    @strawberry.field
    def year(self: dict) -> int | None:
        return self.get("year")

    @strawberry.field
    def date(self: dict) -> date | None:
        return self.get("date")

    @strawberry.field
    def quantity_source(self: dict) -> str | None:
        return self.get("quantity_source")

    @strawberry.field
    def quantity_source_detail(self: dict) -> str | None:
        return self.get("quantity_source_detail")

    @strawberry.field
    def purpose(self: dict) -> str | None:
        return self.get("purpose")

    @strawberry.field
    def iso21931_compliance(self: dict) -> bool | None:
        return self.get("iso21931_compliance")

    @strawberry.field
    def en15978_compliance(self: dict) -> bool | None:
        return self.get("en15978_compliance")

    @strawberry.field
    def rics_2017_compliance(self: dict) -> bool | None:
        return self.get("rics_2017_compliance")

    @strawberry.field
    def rics_2023_compliance(self: dict) -> bool | None:
        return self.get("rics_2023_compliance")

    @strawberry.field
    def ashrae_240p_compliance(self: dict) -> bool | None:
        return self.get("ashrae_240p_compliance")

    @strawberry.field
    def sei_prestandard_compliance(self: dict) -> bool | None:
        return self.get("sei_prestandard_compliance")

    @strawberry.field
    def verified(self: dict) -> bool | None:
        return self.get("verified")

    @strawberry.field
    def verified_info(self: dict) -> str | None:
        return self.get("verified_info")

    @strawberry.field
    def validity_period(self: dict) -> str | None:
        return self.get("validity_period")

    @strawberry.field
    def results_validation_description(self: dict) -> str | None:
        return self.get("results_validation_description")

    @strawberry.field
    def tool_report_upload(self: dict) -> Base64 | None:
        return self.get("tool_report_upload")

    @strawberry.field
    def report_name(self: dict) -> str | None:
        return self.get("report_name")

    @strawberry.field
    def additional_lca_report_name(self: dict) -> str | None:
        return self.get("additional_lca_report_name")

    @strawberry.field
    def project_phase_at_reporting(self: dict) -> str | None:
        return self.get("project_phase_at_reporting")

    @strawberry.field
    def project_phase_at_time_of_assessment(self: dict) -> str | None:
        return self.get("project_phase_at_time_of_assessment")

    @strawberry.field
    def operational_energy_included(self: dict) -> bool | None:
        return self.get("operational_energy_included")

    @strawberry.field
    def biogenic_carbon_included(self: dict) -> bool | None:
        return self.get("biogenic_carbon_included")

    @strawberry.field
    def biogenic_carbon_accounting_method(self: dict) -> str | None:
        return self.get("biogenic_carbon_accounting_method")

    @strawberry.field
    def bio_sustainability_certification(self: dict) -> str | None:
        return self.get("bio_sustainability_certification")

    @strawberry.field
    def biogenic_carbon_description(self: dict) -> str | None:
        return self.get("biogenic_carbon_description")

    @strawberry.field
    def project_refrigerants(self: dict) -> str | None:
        return self.get("project_refrigerants")

    @strawberry.field
    def refrigerant_type_included(self: dict) -> str | None:
        return self.get("refrigerant_type_included")

    @strawberry.field
    def substructure_scope(self: dict) -> str | None:
        return self.get("substructure_scope")

    @strawberry.field
    def shell_superstructure_scope(self: dict) -> str | None:
        return self.get("shell_superstructure_scope")

    @strawberry.field
    def shell_exterior_enclosure_scope(self: dict) -> str | None:
        return self.get("shell_exterior_enclosure_scope")

    @strawberry.field
    def interior_construction_scope(self: dict) -> str | None:
        return self.get("interior_construction_scope")

    @strawberry.field
    def interior_finishes_scope(self: dict) -> str | None:
        return self.get("interior_finishes_scope")

    @strawberry.field
    def services_mechanical_scope(self: dict) -> str | None:
        return self.get("services_mechanical_scope")

    @strawberry.field
    def services_electrical_scope(self: dict) -> str | None:
        return self.get("services_electrical_scope")

    @strawberry.field
    def services_plumbing_scope(self: dict) -> str | None:
        return self.get("services_plumbing_scope")

    @strawberry.field
    def sitework_scope(self: dict) -> str | None:
        return self.get("sitework_scope")

    @strawberry.field
    def equipment_scope(self: dict) -> str | None:
        return self.get("equipment_scope")

    @strawberry.field
    def furnishings_scope(self: dict) -> str | None:
        return self.get("furnishings_scope")

    @strawberry.field
    def lca_requirements(self: dict) -> str | None:
        return self.get("lca_requirements")


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
    @strawberry.field
    def currency(self: dict) -> str | None:
        return self.get("currency")

    @strawberry.field
    def total_cost(self: dict) -> float | None:
        return self.get("total_cost")

    @strawberry.field
    def hard_cost(self: dict) -> float | None:
        return self.get("hard_cost")

    @strawberry.field
    def soft_cost(self: dict) -> float | None:
        return self.get("soft_cost")

    @strawberry.field
    def siteworks_cost(self: dict) -> float | None:
        return self.get("siteworks_cost")

    @strawberry.field
    def cost_source(self: dict) -> str | None:
        return self.get("cost_source")

    @strawberry.field
    def notes(self: dict) -> str | None:
        return self.get("notes")


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
        return self.get("column_grid_long")

    @strawberry.field
    def risk_category(self: dict) -> str | None:
        return self.get("risk_category")

    @strawberry.field
    def live_load(self: dict) -> GraphQLValueUnit | None:
        return self.get("live_load")

    @strawberry.field
    def snow_load(self: dict) -> GraphQLValueUnit | None:
        return self.get("snow_load")

    @strawberry.field
    def wind_speed(self: dict) -> GraphQLValueUnit | None:
        return self.get("wind_speed")

    @strawberry.field
    def earthquake_importance_factor(self: dict) -> float | None:
        return self.get("earthquake_importance_factor")

    @strawberry.field
    def seismic_design_category(self: dict) -> str | None:
        return self.get("seismic_design_category")

    @strawberry.field
    def horizontal_gravity_system(self: dict) -> str | None:
        return self.get("horizontal_gravity_system")

    @strawberry.field
    def secondary_horizontal_gravity_system(self: dict) -> str | None:
        return self.get("secondary_horizontal_gravity_system")

    @strawberry.field
    def vertical_gravity_system(self: dict) -> str | None:
        return self.get("vertical_gravity_system")

    @strawberry.field
    def secondary_vertical_gravity_system(self: dict) -> str | None:
        return self.get("secondary_vertical_gravity_system")

    @strawberry.field
    def lateral_system(self: dict) -> str | None:
        return self.get("lateral_system")

    @strawberry.field
    def podium(self: dict) -> str | None:
        return self.get("podium")

    @strawberry.field
    def allowable_soil_bearing_pressure(self: dict) -> GraphQLValueUnit | None:
        return self.get("allowable_soil_bearing_pressure")

    @strawberry.field
    def foundation_type(self: dict) -> str | None:
        return self.get("foundation_type")


@strawberry.type(name="ProjectMetaData")
class GraphQLProjectMetaData:
    @strawberry.field
    def source(self: dict) -> GraphQLSource | None:
        return GraphQLSource(**self.get("source"))

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
        return self.get("owner")

    @strawberry.field
    def assessment(self: dict) -> GraphQLAssessmentMetaData | None:
        return GraphQLAssessmentMetaData(**self.get("assessment"))

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
        value = self.get("newly_built_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def retrofitted_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("retrofitted_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def demolished_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("demolished_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def existing_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("existing_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def built_floor_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("built_floor_area")
        return GraphQLValueUnit(**value) if value else None

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
        value = self.get("project_work_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def project_site_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("project_site_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def conditioned_floor_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("conditioned_floor_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def unconditioned_floor_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("unconditioned_floor_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def enclosed_parking_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("enclosed_parking_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def detached_parking_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("detached_parking_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def surface_parking_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("surface_parking_area")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def detached_parking_structure_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("detached_parking_structure_area")

        return GraphQLValueUnit(**value) if value else None

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
        value =self.get("mean_roof_height")
        return GraphQLValueUnit(**value) if value else None

    @strawberry.field
    def window_wall_ratio(self: dict) -> float | None:
        return self.get("window_wall_ratio")

    @strawberry.field
    def thermal_envelope_area(self: dict) -> GraphQLValueUnit | None:
        value = self.get("thermal_envelope_area")
        return GraphQLValueUnit(**value) if value else None

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
        return self.get("energy")

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
    def construction_start(self: dict) -> date | None:
        return self.get("construction_start")

    @strawberry.field
    def construction_year_existing_building(self: dict) -> int | None:
        return self.get("construction_year_existing_building")

    @strawberry.field
    def building_occupancy_start(self: dict) -> date | None:
        return self.get("building_occupancy_start")

    @strawberry.field
    def cost(self: dict) -> GraphQLCostMetaData | None:
        return self.get("cost")

    @strawberry.field
    def structural(self: dict) -> GraphQLStructuralMetaData | None:
        return self.get("structural")

    @strawberry.field
    def publication(self: dict) -> GraphQLPublicationMetaData | None:
        return self.get("publication")


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
