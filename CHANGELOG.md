# Changelog

## 1.0.0 (2025-08-20)


### Features

* add enac-it4r GitHub Actions workflows for deployment and release management ([1d2c6ea](https://github.com/globalbuildingdatainitiative/backend/commit/1d2c6eaa15a239af9a917a185558d04d53d0dc2e))
* allow requests from epfl.ch origin in get_origin function ([70d3a8c](https://github.com/globalbuildingdatainitiative/backend/commit/70d3a8ca0f8d2195ab9f17abb2336ca584bed4c7))
* enhance BACKEND_CORS_ORIGINS parsing to support JSON array strings ([ad6eb15](https://github.com/globalbuildingdatainitiative/backend/commit/ad6eb158828c490a681994e5c22016b3dfa1e550))


### Bug Fixes

* add 'stage' branch to deployment trigger in GitHub Actions workflow ([dddd067](https://github.com/globalbuildingdatainitiative/backend/commit/dddd067739bec50c53c0b622f4a9ada02bad21b2))
* **auth:** improve SuperTokens startup reliability and database connectivity ([#125](https://github.com/globalbuildingdatainitiative/backend/issues/125)) ([3b7977f](https://github.com/globalbuildingdatainitiative/backend/commit/3b7977f92ab251515f5881cca423b47119ca14a7))
* change path for deploy-enacit4r.yml ([626e62a](https://github.com/globalbuildingdatainitiative/backend/commit/626e62a8f3cb8c6717b3140db104d7d61de53441))
* **release-please:** replace node by simple for release-type ([27e009f](https://github.com/globalbuildingdatainitiative/backend/commit/27e009f76e8ee55abb9b34cd80cde1aac624c223))
* remove router module from build context in deployment workflow ([471912e](https://github.com/globalbuildingdatainitiative/backend/commit/471912e3937fc3bf5c7b5a41330b75bc66834607))
* update get_origin function to return dynamic CORS origin from settings for all modules ([4d5a36f](https://github.com/globalbuildingdatainitiative/backend/commit/4d5a36faa769c4673d4922c9f9d30ba27d6f64f1))
