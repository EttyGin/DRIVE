NCCL share/68eeae5c-7bfc-8011-b924-296b8cd47b1c

smart log/68ec3ab3-daf8-8011-8f15-838ff8631941

https://github.com/surajssd/llm-k8s/blob/8a7fbb969b1edaa8ab40ee9c35dc3bba62c1a6d6/deepseek-v2.5/02_tp8_pp2_ib/lws.sh#L291-L294
https://docs.vllm.ai/en/v0.8.5/serving/distributed_serving.html
https://docs.vllm.ai/en/v0.8.5/getting_started/troubleshooting.html#troubleshooting-incorrect-hardware-driver
=============
root@deepseek-v2-5-0:/vllm-workspace# bash /vllm-workspace/examples/online_serving/multi-node-serving.sh leader --ray_cluster_size=$LWS_GROUP_SIZE --dashboard-host=0.0.0.0 --metrics-export-port=8080;
https://github.com/vllm-project/vllm/issues/16425
https://discuss.vllm.ai/t/deploying-multi-node-llm-with-infiband-roce/1344/8
research share/68f16d4c-abd8-8011-943c-39a31137e091
https://chatgpt.com/share/68ffecd2-9e34-8011-be12-4406434bcd4a
