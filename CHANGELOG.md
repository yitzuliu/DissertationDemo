# Changelog

All notable changes to the AI Manual Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete project documentation organized in `/docs` directory
- System Architecture Document (`/docs/ARCHITECTURE.md`)
- Model Comparison Guide (`/docs/MODEL_COMPARISON.md`)
- Developer Setup Guide (`/docs/DEVELOPER_SETUP.md`)
- API Documentation (`/docs/API.md`)
- Unified Configuration System with `ConfigManager` class
- Configuration validation and standardization script
- New API endpoints for configuration management
- Standard Model Interface with `BaseVisionModel` abstract class
- Model-specific implementations that follow the standard interface:
  - `Phi3VisionModel` for Phi-3 Vision
  - `YOLO8Model` for YOLO8 object detection
  - `LLaVAModel` for LLaVA via Ollama
  - `SmolVLMModel` for SmolVLM
- Factory class `VLMFactory` for model instantiation

### Changed
- Moved existing documentation from root directory to `/docs` directory
- Enhanced the content of all documentation files with more comprehensive information
- Removed duplicate documentation files from root directory
- Created DOCUMENTATION.md with links to all documentation files
- Refactored image preprocessing into a centralized utility module
- Updated all model implementations to use the unified image preprocessing pipeline

### Fixed
- N/A

## [1.0.0] - 2025-06-23

### Added
- Initial release of AI Manual Assistant
- Support for multiple VLM models:
  - SmolVLM
  - Phi-3 Vision
  - YOLO8
  - LLaVA
  - Moondream2
- Real-time webcam processing
- Web-based user interface
- Model switching capability
- Image preprocessing pipeline
