python -m vllm.entrypoints.openai.api_server \
  --model microsoft/Phi-3-vision-128k-instruct \
  --trust-remote-code \
  --port 8080 \
  --max-model-len 8192