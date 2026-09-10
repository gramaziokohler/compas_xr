# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added Stream Realtime Database Methods and Component
* Added type hints to all public methods and functions
* Added `compas_xr.proto/compas_xr.proto`, the protobuf schema for the MQTT messages, published as a release asset together with the generated bindings for each supported language.
* Added an explicit `JointTrajectory` message, replacing the untyped dict of joint names and values.

### Changed

* Update Grasshopper components to build as CPython 3.x components
* Migrated documentation to Mkdocs format
* Upgraded `compas_pb` to 1.1 and `compas_timber` to its Model-based API.
* Replaced the legacy `compas.datastructures.Assembly`/`Part` integration with `compas_model.models.Model`/`Element`.
* Upgraded `compas_pb` to 1.2, which is where the proto bundling tasks landed.
* **Breaking:** MQTT messages now travel as protobuf instead of COMPAS JSON. A publisher on the new wire cannot be read by a subscriber still on JSON, so every participant in a project has to move together. Pass `JsonMessageCodec()` explicitly to keep the old wire.
* Fixed `Header.parse`, which shifted every field by one and regenerated the timestamp, so device coordination ran on scrambled values.
* Fixed `create_project_data_from_compas`, which emitted `beams`/`joints` instead of `elements` for a `TimberModel`, leaving consumers with a model that appeared to have no elements.

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
