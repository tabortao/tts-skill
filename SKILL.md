---
name: tts-skill
description: 多引擎文本转语音技能，支持Qwen3-TTS本地音色克隆、VoiceCraft在线TTS和OpenAI TTS。使用自然语言指令即可生成高质量语音，支持通过assets下的文件名前缀选择音色。指令模式：/tts-skill [引擎] [文本内容] --voice [音色关键词]
---

# 🎙️ TTS-Skill - 多引擎文本转语音技能

一个功能强大的多引擎TTS技能，支持本地音色克隆、在线TTS服务和商业API，为用户提供完整的语音生成解决方案。

## ✨ 核心功能

### 🚀 多引擎支持
- **🔊 Qwen3-TTS** - 本地音色克隆，支持自定义参考音频
- **🌐 VoiceCraft** - 在线Microsoft Edge TTS，20+种中文语音
- **🎯 OpenAI TTS** - 商业级高质量语音生成

### 🎨 智能特性
- **🧠 语义理解** - 支持自然语言指令，自动匹配音色
- **🌍 语言检测** - 智能识别中英文，自动选择合适引擎
- **🎭 音色匹配** - 通过文件名前缀智能匹配参考音色
- **⚡ 一键生成** - 简化操作流程，快速生成高质量语音

## 📁 文件结构

```
tts-skill/
├── engines/                    # TTS引擎目录
│   ├── qwen3-tts-cli.py       # 千问TTS引擎
│   ├── edge-tts-cli.py        # VoiceCraft引擎
│   ├── openai-tts-cli.py      # OpenAI TTS引擎
│   └── edge-tts.config        # Edge-TTS配置文件
├── assets/                     # 参考音色目录
│   ├── zh/                    # 中文音色
│   │   ├── 赵信.mp3
│   │   ├── 赵信.txt
│   │   ├── 寒冰射手.mp3
│   │   └── 寒冰射手.txt
│   └── en/                    # 英文音色
└── SKILL.md                   # 技能说明文档
```

## 🎯 使用方法

### 📝 基本语法

```
/tts-skill [引擎] [文本内容] --voice [音色关键词] [其他参数]
```

### 🎭 引擎选择

| 引擎 | 指令 | 特点 | 适用场景 |
|------|------|------|----------|
| Qwen3-TTS | `qwen3-tts` | 本地音色克隆 | 个性化语音、参考音色 |
| VoiceCraft | `edge-tts` | 在线多语音 | 快速生成、多种选择 |
| OpenAI TTS | `openai-tts` | 商业级质量 | 专业应用、高质量需求 |

### 🗣️ 自然语言指令示例

```
# 使用赵信音色生成语音
/tts-skill qwen3-tts 胜利在呼唤，勇往直前 --voice 赵信

# 使用微软晓晓朗读
/tts-skill edge-tts 你好，这是一个测试 --voice xiaoxiao

# 使用OpenAI语音生成
/tts-skill openai-tts Hello, this is a test --voice alloy
```

### 🎨 音色选择

**智能匹配规则：**
- 支持通过assets目录下的文件名前缀选择音色
- 当用户说"用赵信的声音"，自动匹配到`assets/赵信.mp3`
- 支持模糊匹配，如"温柔女声"匹配到晓晓音色

**常用音色关键词：**

#### Qwen3-TTS (本地音色)
- `赵信` - 英雄联盟赵信角色音色
- `寒冰射手` - 英雄联盟艾希角色音色
- `Lei` - Lei角色音色
- `布里茨` - 机器人布里茨音色

#### VoiceCraft (微软语音)
**女声：**
- `xiaoxiao` - 晓晓 (温柔)
- `xiaoyi` - 晓伊 (甜美)
- `xiaochen` - 晓辰 (知性)
- `xiaohan` - 晓涵 (优雅)

**男声：**
- `yunxi` - 云希 (清朗)
- `yunyang` - 云扬 (阳光)
- `yunjian` - 云健 (稳重)

#### OpenAI TTS
- `alloy` - 中性平衡
- `echo` - 深沉磁性
- `nova` - 温暖女性

## 🔧 安装配置

### Qwen3-TTS 环境配置

```bash
# 检测是否已配置qwen3-tts环境
micromamba activate qwen3-tts

# 如果未配置，运行安装脚本
python engines/qwen3-tts-cli.py --install

# 手动安装步骤：
# 1. 安装Python 3.12+
# 2. 安装Micromamba
# 3. 创建虚拟环境：micromamba create -n qwen3-tts python=3.12 -y
# 4. 激活环境：micromamba activate qwen3-tts
# 5. 安装包：pip install -U qwen-tts modelscope
# 6. 下载模型：modelscope download --model Qwen/Qwen3-TTS-12Hz-0.6B-Base --local_dir ./Qwen3-TTS-12Hz-0.6B-Base
```

### VoiceCraft 配置

```bash
# 查看可用语音
python engines/edge-tts-cli.py --list-voices

# 查看语音风格
python engines/edge-tts-cli.py --list-styles

# 修改配置文件 engines/edge-tts.config
```

### OpenAI TTS 配置

```bash
# 创建配置文件
[DEFAULT]
api_key = your_openai_api_key
api_url = https://api.openai.com/v1/audio/speech
voice = alloy
model = tts-1
speed = 1.0
```

## 🎮 详细指令

### Qwen3-TTS 引擎

```bash
# 基本使用
python engines/qwen3-tts-cli.py "要转换的文本" --voice 赵信

# 从文件读取
python engines/qwen3-tts-cli.py --text-file input.txt --voice 寒冰射手

# 指定输出路径
python engines/qwen3-tts-cli.py "测试文本" --voice 赵信 --output test.wav

# 列出可用音色
python engines/qwen3-tts-cli.py --list-voices

# 安装环境
python engines/qwen3-tts-cli.py --install
```

### VoiceCraft 引擎

```bash
# 基本使用
python engines/edge-tts-cli.py "测试文本" --voice xiaoxiao

# 调整参数
python engines/edge-tts-cli.py "测试文本" --voice yunxi --speed 1.2 --pitch 5 --style cheerful

# 从文件读取
python engines/edge-tts-cli.py --text-file script.txt --voice xiaohan

# 列出语音选项
python engines/edge-tts-cli.py --list-voices
python engines/edge-tts-cli.py --list-styles
```

### OpenAI TTS 引擎

```bash
# 基本使用
python engines/openai-tts-cli.py "Hello World" --voice alloy

# 使用高质量模型
python engines/openai-tts-cli.py "测试文本" --voice nova --model tts-1-hd --speed 1.5

# 列出选项
python engines/openai-tts-cli.py --list-voices
python engines/openai-tts-cli.py --list-models
```

## 🎯 参数说明

### 通用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--voice` | 音色选择 | `--voice 赵信` |
| `--output` | 输出文件路径 | `--output speech.mp3` |
| `--text-file` | 文本文件输入 | `--text-file script.txt` |

### VoiceCraft 专用参数

| 参数 | 范围 | 默认 | 说明 |
|------|------|------|------|
| `--speed` | 0.5-2.0 | 1.0 | 语速调节 |
| `--pitch` | -50到50 | 0 | 音调调节 |
| `--style` | 见风格列表 | general | 语音风格 |

### OpenAI TTS 专用参数

| 参数 | 范围 | 默认 | 说明 |
|------|------|------|------|
| `--model` | tts-1, tts-1-hd | tts-1 | 模型选择 |
| `--speed` | 0.25-4.0 | 1.0 | 语速调节 |

## 🎨 语音风格

### VoiceCraft 支持风格
- `general` - 通用风格
- `assistant` - 智能助手
- `chat` - 聊天对话
- `customerservice` - 客服专业
- `newscast` - 新闻播报
- `affectionate` - 亲切温暖
- `calm` - 平静舒缓
- `cheerful` - 愉快欢乐
- `gentle` - 温和柔美
- `lyrical` - 抒情诗意
- `serious` - 严肃正式

## 🚀 高级功能

### 🌍 智能语言路由

系统自动检测输入文本语言：
- **中文文本** → 自动选择`assets/zh/`目录下的中文音色
- **英文文本** → 自动选择`assets/en/`目录下的英文音色
- **混合文本** → 根据主要语言自动路由

### 🎭 音色匹配算法

1. **精确匹配** - 完全匹配文件名
2. **模糊匹配** - 包含关键词即匹配
3. **默认回退** - 使用赵信音色作为默认
4. **语言适配** - 根据检测语言选择对应目录

### ⚡ 性能优化

- **Qwen3-TTS** - 支持FlashAttention 2减少GPU内存使用
- **VoiceCraft** - 流式下载，支持大文件处理
- **OpenAI TTS** - 高质量模型选择，平衡速度与质量

## 🔧 故障排除

### 常见问题

**Q: Qwen3-TTS环境配置失败？**
A: 确保已安装Python 3.12+和Micromamba，检查网络连接，可能需要科学上网下载模型。

**Q: VoiceCraft API调用失败？**
A: 检查网络连接，确认API地址正确，尝试使用备用API端点。

**Q: OpenAI TTS认证失败？**
A: 确认API密钥正确，检查账户余额和权限设置。

**Q: 音色匹配不准确？**
A: 确保参考音频文件名清晰明确，避免使用过于相似的名称。

### 调试模式

```bash
# 启用详细输出
python engines/qwen3-tts-cli.py "测试" --voice 赵信 --verbose

# 检查环境
python engines/qwen3-tts-cli.py --check-env

# 测试API连接
python engines/edge-tts-cli.py --test-api
```

## 📈 性能建议

### 硬件要求
- **Qwen3-TTS**: 推荐GPU，最低4GB显存
- **VoiceCraft**: 无特殊要求，依赖网络
- **OpenAI TTS**: 无特殊要求，依赖API

### 使用建议
1. **个性化需求** → 选择Qwen3-TTS本地音色克隆
2. **快速生成** → 选择VoiceCraft在线服务
3. **专业应用** → 选择OpenAI TTS商业API
4. **中文内容** → 优先使用VoiceCraft微软语音
5. **英文内容** → 可选择OpenAI TTS或VoiceCraft

## 🎯 最佳实践

### 音色制作
1. **参考音频** - 选择清晰、无噪音的音频
2. **文本内容** - 提供代表性的文本样本
3. **文件命名** - 使用描述性的文件名便于匹配
4. **格式要求** - 音频MP3/WAV，文本UTF-8编码

### 参数调优
1. **语速调节** - 根据内容类型调整合适语速
2. **音调设置** - 匹配目标角色的音调特征
3. **风格选择** - 根据应用场景选择合适风格

## 🔄 更新日志

### v1.0.0
- 🎉 初始版本发布
- ✅ 支持Qwen3-TTS本地音色克隆
- ✅ 集成VoiceCraft在线TTS服务
- ✅ 添加OpenAI TTS商业API支持
- ✅ 实现智能语言检测和音色匹配
- ✅ 提供自然语言指令支持

---

**🎙️ TTS-Skill** - 让文字拥有声音，让创意更有温度！

*从本地音色克隆到在线TTS服务，AI驱动的多引擎语音生成解决方案。*