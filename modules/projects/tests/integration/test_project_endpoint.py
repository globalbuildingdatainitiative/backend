import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_projects_query(client: AsyncClient, contributions, projects):
    query = """
        query {
            projects {
                items {
                    id
                    name
                    assemblies {
                        id
                        name
                        unit
                        products {
                            id
                            name
                            impactData {
                                ...on EPD {
                                    id
                                }                        
                            }
                            referenceServiceLife
                        }
                    }
                }
                count
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("items")
    assert len(data.get("data", {}).get("projects", {}).get("items")) == len(projects)
    assert data.get("data", {}).get("projects", {}).get("count") == len(projects)
    assert data.get("data", {}).get("projects", {}).get("items", [])[0].get("assemblies")


@pytest.mark.asyncio
async def test_projects_query_filter(client: AsyncClient, contributions, projects):
    query = """
        query($id: UUID!) {
            projects {
                items(filterBy: {equal: {id: $id}}) {
                    id
                    name
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query, "variables": {"id": str(projects[0].id)}},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert len(data.get("data", {}).get("projects", {}).get("items")) == 1
    assert data.get("data", {}).get("projects", {}).get("items", [])[0].get("id") == str(projects[0].id)


@pytest.mark.asyncio
async def test_projects_query_sort(client: AsyncClient, contributions, projects):
    query = """
        query {
            projects {
                items(sortBy: {dsc: "name"}) {
                    id
                    name
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("items")
    assert data.get("data", {}).get("projects", {}).get("items", []) == [
        project.model_dump(include={"id", "name"}, mode="json") for project in sorted(projects, key=lambda p: p.name)
    ]


@pytest.mark.asyncio
async def test_projects_query_offset(client: AsyncClient, contributions, projects):
    query = """
        query {
            projects {
                items(offset: 2) {
                    id
                    name
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("items")
    assert data.get("data", {}).get("projects", {}).get("items", [])[0].get("id") == str(projects[2].id)


@pytest.mark.asyncio
@pytest.mark.parametrize("group_by", ["name", "location.country"])
async def test_projects_query_groups(client: AsyncClient, contributions, projects, group_by):
    query = """
        query($groupBy: String!) {
            projects {
                groups(groupBy: $groupBy) {
                    group
                    items(limit: 2) {
                        id
                        name
                    }
                    count
                }  
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"groupBy": group_by},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("groups")
    assert len(data.get("data", {}).get("projects", {}).get("groups")[0].get("items", [])) == 2


@pytest.mark.asyncio
async def test_projects_query_aggregate(client: AsyncClient, contributions, projects):
    query = """
        query($aggregation: JSON!) {
            projects {
                aggregation(apply: $aggregation)
            }
        }
    """

    aggregation = [{"$group": {"_id": None, "value": {"$avg": "$referenceStudyPeriod"}}}]

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query, "variables": {"aggregation": aggregation}},
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("aggregation")
    assert data.get("data", {}).get("projects", {}).get("aggregation", [])[0].get("value") == 50


@pytest.mark.asyncio
async def test_projects_query_group_aggregate(client: AsyncClient, contributions, projects):
    query = """
        query($groupBy: String!) {
            projects {
                groups(groupBy: $groupBy) {
                    group
                    items {
                        id
                    }
                    aggregation(apply: [{method: AVG, field: "referenceStudyPeriod"}]) {
                        method
                        field
                        value
                    }
                    count
                }  
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"groupBy": "name"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("groups")
    assert (
        data.get("data", {}).get("projects", {}).get("groups")[0].get("aggregation", [])[0].get("field")
        == "referenceStudyPeriod"
    )


@pytest.mark.asyncio
async def test_projects_query_aggregation_advanced(client: AsyncClient, contributions, projects):
    query = """
        query($aggregation: JSON!) {
            projects {
                aggregation(apply: $aggregation)
            }
        }
    """

    aggregation = [
        {
            "$group": {
                "_id": "$name",
                "items": {"$push": "$$ROOT"},
                "count": {"$sum": 1},
                "average": {"$avg": "$referenceStudyPeriod"},
            }
        },
        {
            "$project": {
                "_id": None,
                "group": "name",
                "items": "$items",
                "count": "$count",
                "average": "$average",
            }
        },
    ]
    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"aggregation": aggregation},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("aggregation")
    assert data.get("data", {}).get("projects", {}).get("aggregation", [])[0].get("average") == 50


@pytest.mark.asyncio
async def test_project_metadata_query(client: AsyncClient, metadata_project):
    query = """
        query {
            projects {
                items {
                    id
                    name
                    metaData {
                      source {
                        name
                        url
                      }
                      productClassificationSystem
                      climateZone
                      owner {
                        contact
                        web
                        country
                        email
                        type
                        representative
                      }
                      assessment {
                        assessmentMethodologyDescription
                        uncertainty
                        cutoffMethod
                        assessor {
                          name
                          email
                          organization
                        }
                        year
                        date
                        quantitySource
                        quantitySourceDetail
                        purpose
                        iso21931Compliance
                        en15978Compliance
                        rics2017Compliance
                        rics2023Compliance
                        ashrae240pCompliance
                        seiPrestandardCompliance
                        verified
                        verifiedInfo
                        validityPeriod
                        resultsValidationDescription
                        toolReportUpload
                        reportName
                        additionalLcaReportName
                        projectPhaseAtReporting
                        projectPhaseAtTimeOfAssessment
                        operationalEnergyIncluded
                        biogenicCarbonIncluded
                        biogenicCarbonAccountingMethod
                        bioSustainabilityCertification
                        biogenicCarbonDescription
                        projectRefrigerants
                        refrigerantTypeIncluded
                        substructureScope
                        shellSuperstructureScope
                        shellExteriorEnclosureScope
                        interiorConstructionScope
                        interiorFinishesScope
                        servicesMechanicalScope
                        servicesElectricalScope
                        servicesPlumbingScope
                        siteworkScope
                        equipmentScope
                        furnishingsScope
                        lcaRequirements
                      }
                      lcaSoftwareVersion
                      lcaDatabase
                      lcaDatabaseVersion
                      lcaDatabaseOther
                      lcaModelType
                      interstitialFloors
                      newlyBuiltArea {
                        value
                        unit
                      }
                      retrofittedArea {
                        value
                        unit
                      }
                      demolishedArea {
                        value
                        unit
                      }
                      existingArea {
                        value
                        unit
                      }
                      builtFloorArea {
                        value
                        unit
                      }
                      buildingProjectConstructionType2
                      infrastructureProjectConstructionType
                      infrastructureSectorType
                      buildingUseType
                      infrastructureUseType
                      projectWorkArea {
                        value
                        unit
                      }
                      projectSiteArea {
                        value
                        unit
                      }
                      conditionedFloorArea {
                        value
                        unit
                      }
                      unconditionedFloorArea {
                        value
                        unit
                      }
                      enclosedParkingArea {
                        value
                        unit
                      }
                      detachedParkingArea {
                        value
                        unit
                      }
                      surfaceParkingArea {
                        value
                        unit
                      }
                      detachedParkingStructureArea {
                        value
                        unit
                      }
                      ibcConstructionType
                      projectSurroundings
                      projectHistoric
                      fullTimeEquivalent
                      occupantLoad
                      meanRoofHeight {
                        value
                        unit
                      }
                      windowWallRatio
                      thermalEnvelopeArea {
                        value
                        unit
                      }
                      residentialUnits
                      bedroomCount
                      projectExpectedLife
                      resultsValidatedAsBuilt
                      resultsValidatedAsBuiltDescription
                      assessmentCutoffType
                      assessmentCutoff
                      assessmentCostCutoff
                      heritageStatus
                      omniclassConstructionEntity
                      energy {
                        toolEnergyModeling
                        toolEnergyModelingVersion
                        energyModelMethodologyReference
                        gwpEnergySourcesYear
                        siteLocationWeatherData
                        electricityProvider
                        electricitySource
                        electricityCarbonFactor
                        electricityCarbonFactorSource
                      }
                      architectOfRecord
                      projectUserStudio
                      generalContractor
                      mepEngineer
                      sustainabilityConsultant
                      structuralEngineer
                      civilEngineer
                      landscapeConsultant
                      interiorDesigner
                      otherProjectTeam
                      workCompletionYear
                      constructionStart
                      constructionYearExistingBuilding
                      buildingOccupancyStart
                      cost {
                        currency
                        totalCost
                        hardCost
                        softCost
                        siteworksCost
                        costSource
                        notes
                      }
                      structural {
                        columnGridLong {
                          value
                          unit
                        }
                        riskCategory
                        liveLoad {
                          value
                          unit
                        }
                        snowLoad {
                          value
                          unit
                        }
                        windSpeed {
                          value
                          unit
                        }
                        earthquakeImportanceFactor
                        seismicDesignCategory
                        horizontalGravitySystem
                        secondaryHorizontalGravitySystem
                        verticalGravitySystem
                        secondaryVerticalGravitySystem
                        lateralSystem
                        podium
                        allowableSoilBearingPressure {
                          value
                          unit
                        }
                        foundationType
                      }
                      publication {
                        authors
                        year
                        doi
                        title
                        publisher
                      }
                    }
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("items")
