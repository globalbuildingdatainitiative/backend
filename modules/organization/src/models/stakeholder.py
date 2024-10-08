import strawberry
from enum import Enum


@strawberry.enum
class StakeholderEnum(Enum):
    BUILDING_DATA_OWNERS = "Building data owners"
    DESIGN_PROFESSIONALS = "Building design professionals (architects, engineers)"
    LCA_TOOL_DEVELOPERS = "Building design / LCA tool developers and providers"
    LCA_CONSULTANTS = "Building LCA consultants and service providers"
    BUILDING_USERS = "Building users"
    CIVIL_SOCIETY = "Civil society"
    CLIENTS_INVESTORS_OWNERS = "Clients / inventors / owners (of building data)"
    CONSTRUCTION_COMPANIES = "Construction companies"
    CONSTRUCTION_PRODUCT_MANUFACTURERS = "Construction product manufacturers"
    FACILITY_MANAGERS = "Facility managers"
    FINANCIAL_SERVICE_PROVIDERS = "Financial service providers / insurance companies"
    FUNDING_SYSTEM_DEVELOPERS = "Funding (system) developers and providers"
    STANDARDIZATION_BODIES = "Inter / National standardization bodies"
    MEDIA_REPRESENTATIVES = "Media representatives"
    POLICY_LAW_MAKERS = "Policy and law makers, regulators (national, local)"
    PRODUCT_LCA_DATABASE_DEVELOPERS = "Product LCA database developers"
    PRODUCT_LCA_EPD_DATA_DEVELOPERS = "Product LCA/EPD data developers"
    RESEARCHERS = "Researchers (basic / applied building LCA research)"
    SURVEYORS_VALUATION_PROFESSIONALS = "Surveyors, valuation professionals"
    SUSTAINABILITY_ASSESSMENT_SYSTEM_DEVELOPERS = "Sustainability assessment system developers and providers"
    SUSTAINABILITY_AUDITORS = "Sustainability assessors/auditors"
    ESG_CONSULTANTS = "Sustainability / ESG consultants and service providers"
