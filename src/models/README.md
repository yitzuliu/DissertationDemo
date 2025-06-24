# AI Vision Model Structure

This directory contains the implementation of various vision-language models used in the AI Manual Assistant project.

## Directory Structure

After refactoring, the models are organized in the following structure:

```
models/
├── base_model.py         # Base abstract class and factory
├── phi3_vision/          # PHI-3 Vision model implementation
│   ├── __init__.py
│   └── phi3_vision_model.py
├── LLava/                # LLaVA model implementation
│   ├── __init__.py
│   └── llava_model.py
├── smolvlm/              # SmolVLM model implementation
│   ├── __init__.py
│   └── smolvlm_model.py
└── yolo8/                # YOLO8 model implementation
    ├── __init__.py
    └── yolo8_model.py
```

## Model Usage

All models implement the `BaseVisionModel` abstract base class, which provides a consistent interface for model initialization, prediction, and management.

To use a model:

```python
from models.base_model import VLMFactory

# Create a model instance using the factory
model = VLMFactory.create_model(model_name, config)

# Load the model
model.load_model()

# Process an image with a prompt
result = model.predict(image, prompt, options)
```

## Adding New Models

To add a new model:

1. Create a new directory for your model under `models/`
2. Create an `__init__.py` file to make it a proper package
3. Create a model implementation file (e.g., `my_model_model.py`)
4. Implement the model class by extending `BaseVisionModel`
5. Add your model to the `VLMFactory.create_model()` method in `base_model.py`
