# Qwen3-TTS 安装与使用指南

本文档介绍如何使用 Micromamba 安装 Qwen3-TTS，并使用 Qwen3-TTS-12Hz-0.6B-Base 模型进行语音克隆。

## 环境准备

### 前提条件
- 已安装 Micromamba（本指南假设您已完成安装）
- 具备 NVIDIA GPU 和 CUDA 支持（推荐）
- Python 3.12 环境

### 创建虚拟环境

```bash
# 创建 Qwen3-TTS 专用环境
micromamba create -n qwen3-tts python=3.12 -y

# 激活环境
micromamba activate qwen3-tts
```

## 安装依赖包

### 安装 Qwen3-TTS 核心包

```bash
pip install -U qwen-tts
```

### 安装 FlashAttention 2（强烈推荐）

FlashAttention 2 可以显著减少 GPU 内存使用，提高推理效率：

```bash
# 标准安装
pip install -U flash-attn --no-build-isolation

# 如果机器内存小于 96GB 但 CPU 核心较多
MAX_JOBS=4 pip install -U flash-attn --no-build-isolation
```

> **注意**：请确保您的硬件兼容 FlashAttention 2。具体要求请参考 [FlashAttention 官方文档](https://github.com/Dao-AILab/flash-attention)。

## Qwen3-TTS-12Hz-0.6B-Base 模型使用

### 模型简介

**Qwen3-TTS-12Hz-0.6B-Base** 是一个轻量级基础模型，具有以下特点：
- 🔊 **快速语音克隆**：仅需 3 秒音频即可克隆目标声音
- 🌍 **多语言支持**：支持中文、英文、日文、韩文、德文、法文、俄文、葡萄牙文、西班牙文、意大利文
- ⚡ **流式生成**：支持实时流式语音合成
- 💡 **轻量高效**：0.6B 参数量，适合资源受限环境

### 基础使用示例

```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# 加载 Qwen3-TTS-12Hz-0.6B-Base 模型
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
    device_map="cuda:0",           # 使用 GPU
    dtype=torch.bfloat16,          # 使用 bfloat16 精度
    attn_implementation="flash_attention_2",  # 启用 FlashAttention 2
)

# 准备参考音频和文本
ref_audio = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/clone.wav"
ref_text = "Okay. Yeah. I resent you. I love you. I respect you. But you know what? You blew it! And thanks to you."

# 执行语音克隆
wavs, sr = model.generate_voice_clone(
    text="I am solving the equation: x = [-b ± √(b²-4ac)] / 2a? Nobody can — it's a disaster (◍•͈⌔•͈◍), very sad!",
    language="English",
    ref_audio=ref_audio,
    ref_text=ref_text,
)

# 保存生成的音频文件
sf.write("output_voice_clone.wav", wavs[0], sr)
print("语音克隆完成！输出文件：output_voice_clone.wav")
```

### 高级用法：可复用的语音克隆提示

如果您需要多次使用相同的参考音频，可以预先创建语音克隆提示以提高效率：

```python
# 创建可复用的语音克隆提示
prompt_items = model.create_voice_clone_prompt(
    ref_audio=ref_audio,
    ref_text=ref_text,
    x_vector_only_mode=False,  # 使用完整模式以获得更好的克隆质量
)

# 批量生成多个句子
sentences = [
    "This is the first sentence.",
    "Here comes the second one.",
    "And finally, the third sentence."
]

languages = ["English", "English", "English"]

wavs, sr = model.generate_voice_clone(
    text=sentences,
    language=languages,
    voice_clone_prompt=prompt_items,
)

# 保存所有生成的音频
for i, wav in enumerate(wavs):
    sf.write(f"output_batch_{i+1}.wav", wav, sr)
```

## 启动本地 Web UI 演示

Qwen3-TTS 提供了便捷的 Web 界面，便于交互式使用：

```bash
# 启动 Web UI 服务
qwen-tts-demo Qwen/Qwen3-TTS-12Hz-0.6B-Base --ip 0.0.0.0 --port 8000
```

启动后，在浏览器中访问：
```
http://localhost:8000
```

### HTTPS 配置（可选）

为避免浏览器麦克风权限问题，建议对 Base 模型使用 HTTPS：

```bash
# 生成自签名证书
openssl req -x509 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=localhost"

# 使用 HTTPS 启动服务
qwen-tts-demo Qwen/Qwen3-TTS-12Hz-0.6B-Base \
  --ip 0.0.0.0 --port 8000 \
  --ssl-certfile cert.pem \
  --ssl-keyfile key.pem \
  --no-ssl-verify
```

然后通过 HTTPS 访问：
```
https://localhost:8000
```

## 手动下载模型权重

如果您的运行环境不适合在运行时下载权重，可以手动下载模型到本地：

### 通过 ModelScope 下载（中国大陆用户推荐）

```bash
pip install -U modelscope

modelscope download --model Qwen/Qwen3-TTS-Tokenizer-12Hz --local_dir ./Qwen3-TTS-Tokenizer-12Hz
modelscope download --model Qwen/Qwen3-TTS-12Hz-0.6B-Base --local_dir ./Qwen3-TTS-12Hz-0.6B-Base
```

### 通过 Hugging Face 下载

```bash
pip install -U "huggingface_hub[cli]"

huggingface-cli download Qwen/Qwen3-TTS-Tokenizer-12Hz --local-dir ./Qwen3-TTS-Tokenizer-12Hz
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-Base --local-dir ./Qwen3-TTS-12Hz-0.6B-Base
```

## 常见问题与解决方案

### 1. GPU 内存不足
- ✅ 启用 FlashAttention 2
- ✅ 使用 `dtype=torch.bfloat16` 或 `torch.float16`
- ✅ 减小批量大小

### 2. 安装 flash-attn 失败
- ✅ 确保已安装正确版本的 CUDA 工具包
- ✅ 尝试降低 MAX_JOBS 数值
- ✅ 参考官方文档检查硬件兼容性

### 3. 模型下载缓慢
- ✅ 使用 ModelScope 镜像（中国大陆用户）
- ✅ 手动下载模型权重到本地

## 参考资源

- 📚 [Qwen3-TTS 官方文档](https://github.com/QwenLM/Qwen3-TTS)
- 🤗 [Hugging Face 模型库](https://huggingface.co/collections/Qwen/qwen3-tts)
- 🤖 [ModelScope 模型库](https://modelscope.cn/collections/Qwen/Qwen3-TTS)
- 📄 [技术博客](https://qwen.ai/blog?id=qwen3tts-0115)
- 📑 [论文](https://arxiv.org/abs/2601.15621)

---

**提示**：Qwen3-TTS-12Hz-0.6B-Base 是一个功能强大的基础模型，特别适合快速语音克隆场景。如需更多高级功能（如语音设计、自定义音色等），可以考虑使用其他专业模型版本。