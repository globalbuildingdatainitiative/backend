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
    a0: float | None = None
    a1a3: float | None = None
    a4: float | None = None
    a5: float | None = None
    b1: float | None = None
    b2: float | None = None
    b3: float | None = None
    b4: float | None = None
    b5: float | None = None
    b6: float | None = None
    b7: float | None = None
    b8: float | None = None
    c1: float | None = None
    c2: float | None = None
    c3: float | None = None
    c4: float | None = None
    d: float | None = None
    total: float | None = None


@strawberry.type(name="Results")
class GraphQLResults:
    gwp: GraphQLImpactCategoryResults | None = None
    gwp_fos: GraphQLImpactCategoryResults | None = None
    gwp_bio: GraphQLImpactCategoryResults | None = None
    gwp_lul: GraphQLImpactCategoryResults | None = None
    odp: GraphQLImpactCategoryResults | None = None
    ap: GraphQLImpactCategoryResults | None = None
    ep: GraphQLImpactCategoryResults | None = None
    ep_fw: GraphQLImpactCategoryResults | None = None
    ep_mar: GraphQLImpactCategoryResults | None = None
    ep_ter: GraphQLImpactCategoryResults | None = None
    pocp: GraphQLImpactCategoryResults | None = None
    adpe: GraphQLImpactCategoryResults | None = None
    adpf: GraphQLImpactCategoryResults | None = None
    penre: GraphQLImpactCategoryResults | None = None
    pere: GraphQLImpactCategoryResults | None = None
    perm: GraphQLImpactCategoryResults | None = None
    pert: GraphQLImpactCategoryResults | None = None
    penrt: GraphQLImpactCategoryResults | None = None
    penrm: GraphQLImpactCategoryResults | None = None
    sm: GraphQLImpactCategoryResults | None = None
    pm: GraphQLImpactCategoryResults | None = None
    wdp: GraphQLImpactCategoryResults | None = None
    irp: GraphQLImpactCategoryResults | None = None
    etp_fw: GraphQLImpactCategoryResults | None = None
    htp_c: GraphQLImpactCategoryResults | None = None
    htp_nc: GraphQLImpactCategoryResults | None = None
    sqp: GraphQLImpactCategoryResults | None = None
    rsf: GraphQLImpactCategoryResults | None = None
    nrsf: GraphQLImpactCategoryResults | None = None
    fw: GraphQLImpactCategoryResults | None = None
    hwd: GraphQLImpactCategoryResults | None = None
    nhwd: GraphQLImpactCategoryResults | None = None
    rwd: GraphQLImpactCategoryResults | None = None
    cru: GraphQLImpactCategoryResults | None = None
    mrf: GraphQLImpactCategoryResults | None = None
    mer: GraphQLImpactCategoryResults | None = None
    eee: GraphQLImpactCategoryResults | None = None
    eet: GraphQLImpactCategoryResults | None = None


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
    reference_service_life: strawberry.auto
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
        return countries.get(self.country.value).name

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
    name: str | None = None
    email: str | None = None
    organization: str | None = None


@strawberry.type(name="AssessmentMetaData")
class GraphQLAssessmentMetaData:
    assessment_methodology_description: str | None = None
    uncertainty: float | None = None
    cutoff_method: str | None = None
    assessor: GraphQLAssessor | None = None
    year: int | None = None
    date: date | None
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
    contact: str | None = None
    web: str | None = None
    country: str | None = None
    email: str | None = None
    type: str | None = None
    representative: str | None = None


@strawberry.type(name="Energy")
class GraphQLEnergyMetaData:
    tool_energy_modeling: str | None = None
    tool_energy_modeling_version: str | None = None
    enery_model_methodology_reference: str | None = None
    gwp_energy_sources_year: float | None = None
    site_location_weather_data: str | None = None
    electricity_provider: str | None = None
    electricity_source: str | None = None
    electricity_carbon_factor: float | None = None
    electricity_carbon_factor_source: str | None = None


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
    authors: str | None = None
    year: int | None = None
    doi: str | None = None
    title: str | None = None
    publisher: str | None = None


@strawberry.type(name="Structural")
class GraphQLStructuralMetaData:
    column_grid_long: GraphQLValueUnit | None = None
    risk_category: str | None = None
    live_load: GraphQLValueUnit | None = None
    snow_load: GraphQLValueUnit | None = None
    wind_speed: GraphQLValueUnit | None = None
    earthquake_importance_factor: float | None = None
    seismic_design_category: str | None = None
    horizontal_gravity_system: str | None = None
    secondary_horizontal_gravity_system: str | None = None
    vertical_gravity_system: str | None = None
    secondary_vertical_gravity_system: str | None = None
    lateral_system: str | None = None
    podium: str | None = None
    allowable_soil_bearing_pressure: GraphQLValueUnit | None = None
    foundation_type: str | None = None


@strawberry.type(name="ProjectMetaData")
class GraphQLProjectMetaData:
    product_classification_system: str | None = None
    image: Base64 | None = None
    climate_zone: str | None = None
    owner: GraphQLOwnerMetaData | None = None
    assessment: GraphQLAssessmentMetaData | None = None
    lca_software_version: str | None = None
    lca_database: str | None = None
    lca_database_version: str | None = None
    lca_database_other: str | None = None
    lca_model_type: str | None = None
    interstitial_floors: str | None = None
    newly_built_area: GraphQLValueUnit | None = None
    retrofitted_area: GraphQLValueUnit | None = None
    demolished_area: GraphQLValueUnit | None = None
    existing_area: GraphQLValueUnit | None = None
    built_floor_area: GraphQLValueUnit | None = None
    building_project_construction_type_2: str | None = None
    infrastructure_project_construction_type: str | None = None
    infrastructure_sector_type: str | None = None
    building_use_type: str | None = None
    infrastructure_use_type: str | None = None
    project_work_area: GraphQLValueUnit | None = None
    project_site_area: GraphQLValueUnit | None = None
    conditioned_floor_area: GraphQLValueUnit | None = None
    unconditioned_floor_area: GraphQLValueUnit | None = None
    enclosed_parking_area: GraphQLValueUnit | None = None
    detached_parking_area: GraphQLValueUnit | None = None
    surface_parking_area: GraphQLValueUnit | None = None
    detached_parking_structure_area: GraphQLValueUnit | None = None
    ibc_construction_type: str | None = None
    project_surroundings: str | None = None
    project_historic: bool | None = None
    full_time_equivalent: float | None = None
    occupant_load: float | None = None
    mean_roof_height: GraphQLValueUnit | None = None
    window_wall_ratio: float | None = None
    thermal_envelope_area: GraphQLValueUnit | None = None
    residential_units: int | None = None
    bedroom_count: int | None = None
    project_expected_life: int | None = None
    results_validated_as_built: bool | None = None
    results_validated_as_built_description: str | None = None
    assessment_cutoff_type: str | None = None
    assessment_cutoff: str | None = None
    assessment_cost_cutoff: str | None = None
    heritage_status: str | None = None
    omniclass_construction_entity: str | None = None
    energy: GraphQLEnergyMetaData | None = None
    architect_of_record: str | None = None
    project_user_studio: str | None = None
    general_contractor: str | None = None
    mep_engineer: str | None = None
    sustainability_consultant: str | None = None
    structural_engineer: str | None = None
    civil_engineer: str | None = None
    landscape_consultant: str | None = None
    interior_designer: str | None = None
    other_project_team: str | None = None
    work_completion_year: int | None = None
    construction_start: date | None = None
    construction_year_existing_building: int | None = None
    building_occupancy_start: date | None = None
    cost: GraphQLCostMetaData | None = None
    structural: GraphQLStructuralMetaData | None = None
    publication: GraphQLPublicationMetaData | None = None


@strawberry.experimental.pydantic.type(model=LCAxProject, name="Project")
class GraphQLProject:
    assemblies: list[GraphQLAssembly]
    classification_system: strawberry.auto
    comment: strawberry.auto
    description: strawberry.auto
    format_version: str = '0.2.0'
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
