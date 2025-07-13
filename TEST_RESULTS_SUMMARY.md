# VLM Test Results Summary (2025-07-13)

**Source File**: `src/testing/results/test_results_20250713_142116.json`

This table summarizes the performance metrics for each model tested on a MacBook Air M3 (16GB).

# On-Device VLM Model Performance Summary

| **Model Name**                 | **Load Time (s)** | **Avg. Inference Time (s)** | **Memory Δ (GB)** | **Successful Runs** | **Failed Runs** | **Notes**
|-------------------------------|:------------------:|:----------------------------:|:-----------------:|:--------------------:|:--------------:|
| **Moondream2**                | 5.02               | **5.16**                     | **−1.15**         | 3                    | 0              | Fastest inference; negative memory diff suggests memory release.
| **LLaVA-v1.6-Mistral-7B-MLX** | 3.14               | 5.76                         | −0.09             | 1                    | 2              | Failed on synthetic images due to a library bug.
| **Phi-3.5-Vision-Instruct**   | **2.06**           | 10.43                        | −0.04             | 3                    | 0              | Fastest model to load.
| **SmolVLM-500M-Instruct**     | 3.71               | 10.68                        | +0.04             | 3                    | 0              | Reliable and balanced.
| **SmolVLM2-500M-Video-Instruct** | 2.86            | 11.62                        | +0.07             | 3                    | 0              | Consistent performance.

## Key Takeaways

- **Performance**: `Moondream2` is the fastest for inference, while `Phi-3.5-Vision` loads the quickest.
- **Reliability**: All models performed reliably except for `LLaVA-v1.6-MLX`, which has a specific, known issue with non-photographic images.
- **Memory**: Most models had a negligible memory impact. `Moondream2` showed a significant memory decrease, which may indicate efficient memory management or an anomaly in measurement during its test cycle. 