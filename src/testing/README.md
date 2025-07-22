# Testing Directory Overview

This README provides an overview of the reorganized `src/testing/` directory structure, the purpose of each subfolder, and maintenance suggestions for a clean and scalable testing environment.

---

## Directory Structure (Recommended)

```
src/testing/
├── rag/                  # Retrieval-Augmented Generation (RAG) tests
│   ├── rag_module.py
│   └── README.md
│
├── vqa/                  # Visual Question Answering (VQA) tests
│   ├── vqa_framework.py
│   ├── vqa_test.py
│   ├── vqa_README.md
│   ├── vqa_test_result.md
│   └── ...
│
├── vlm/                  # Vision-Language Model (VLM) tests
│   ├── vlm_tester.py
│   ├── vlm_context_tester.py
│   ├── vlm_performance_testing_plan.md
│   └── ...
│
├── results/              # All test outputs and logs
│   └── ...
│
├── materials/            # Test materials (images, datasets, question sets)
│   ├── vqa2/
│   └── images/
│
├── summary/              # Test summaries and analysis reports
│   ├── context_understanding_test_results_summary.md
│   └── model_active.md
│
└── __pycache__/          # Python bytecode cache (can be ignored)
```

---

## Folder Purposes

- **rag/**: All RAG-related modules, scripts, and documentation.
- **vqa/**: All VQA test frameworks, scripts, results, and documentation.
- **vlm/**: All VLM test runners, context testers, performance plans, and related files.
- **results/**: Centralized storage for all test outputs, logs, and intermediate results.
- **materials/**: All test datasets, images, and question sets (e.g., COCO, VQA2, sample images).
- **summary/**: High-level test summaries, model status, and analysis reports.
- **__pycache__/**: Python cache files (auto-generated, can be ignored or cleaned regularly).

---

## Migration Plan

1. Move `RAG/` to `rag/`.
2. Move all VQA-related scripts and docs to `vqa/`.
3. Move all VLM-related scripts and docs to `vlm/`.
4. Move `testing_material/` contents to `materials/`.
5. Move all test outputs to `results/`.
6. Move summary/analysis markdown files to `summary/`.
7. Update all import paths in scripts to reflect the new structure.

---

## Maintenance Suggestions

- Keep each test domain in its own folder for clarity and scalability.
- Store all test outputs in `results/` for easy tracking and comparison.
- Place all datasets and images in `materials/` to avoid duplication.
- Add or update a README in each subfolder to explain its purpose and usage.
- Clean up `__pycache__/` and unused files regularly.

---

For any questions or to propose further improvements, please update this README or contact the maintainers. 