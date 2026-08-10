# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added Stream Realtime Database Methods and Component
* Added type hints to all public methods and functions

### Changed

* Update Grasshopper components to build as CPython 3.x components
* Migrated documentation to Mkdocs format
* Upgraded `compas_pb` to 1.1 and `compas_timber` to its Model-based API.
* Replaced the legacy `compas.datastructures.Assembly`/`Part` integration with `compas_model.models.Model`/`Element`.

### Removed

* Removed Support for IronPython 2.7 support
* Refactored RealtimeDatabase and Storage Classes to path based references.
* Removes dependency on `compas_fab`
* Removed Rhino 7 post installation hooks
* Removed the legacy `AssemblyExtensions` API in favor of `ModelExtensions`.

## [1.0.0] 2024-06-26

### Added

### Changed

### Removed


## [0.9.5] 2024-06-24

### Added

### Changed

### Removed


## [0.9.4] 2024-06-24

### Changed

* Fixed missing dependency for GH.

## [0.9.3] 2024-06-24

### Added

* Add GH components to release.


## [0.9.2] 2024-06-24

### Added

### Changed

### Removed


## [0.9.1] 2024-06-24

* Zenodo DOI generation.

## [0.9.0] 2024-06-24

* Initial release.
