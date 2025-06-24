
Inference with MLX

To run SmolVLM2 with MLX on Apple Silicon devices using Python, you can use the excellent mlx-vlm library. First, you need to install mlx-vlm from this branch using the following command:

pip install git+https://github.com/pcuenca/mlx-vlm.git@smolvlm

Then you can run inference on a single image using the following one-liner, which uses the unquantized 500M version of SmolVLM2:

python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM2-500M-Video-Instruct-mlx \
  --image https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg \
  --prompt "Can you describe this image?"

We also created a simple script for video understanding. You can use it as follows:

python -m mlx_vlm.smolvlm_video_generate \
  --model mlx-community/SmolVLM2-500M-Video-Instruct-mlx \
  --system "Focus only on describing the key dramatic action or notable event occurring in this video segment. Skip general context or scene-setting details unless they are crucial to understanding the main action." \
  --prompt "What is happening in this video?" \
  --video /Users/pedro/Downloads/IMG_2855.mov \
  --prompt "Can you describe this image?"

Note that the system prompt is important to bend the model to the desired behaviour. You can use it to, for example, describe all scenes and transitions, or to provide a one-sentence summary of what's going on.

Citation information
@article{marafioti2025smolvlm,
  title={SmolVLM: Redefining small and efficient multimodal models}, 
  author={Andrés Marafioti and Orr Zohar and Miquel Farré and Merve Noyan and Elie Bakouch and Pedro Cuenca and Cyril Zakka and Loubna Ben Allal and Anton Lozhkov and Nouamane Tazi and Vaibhav Srivastav and Joshua Lochner and Hugo Larcher and Mathieu Morlon and Lewis Tunstall and Leandro von Werra and Thomas Wolf},
  journal={arXiv preprint arXiv:2504.05299},
  year={2025}
}
