# tts-skill设计方案

实现本地使用Qwen3-TTS-12Hz-0.6B-Base克隆声音、使用VoiceCraft调用在线生成语音。

## tts-skill设计

使用skill-creator技能，参考test_qwen3_tts_final.py、Qwen3-TTS-Installation-Guide，创建一个tts-skill技能，文件结构如下：

## 文件结构

```powershell
engines/ # engines文件夹，插件化设计，为来可以集成更多的tts
engines/qwen3-tts-cli.py  #对接qwen3-tts
engines/edge-tts-cli.py #对接VoiceCraft https://github.com/tabortao/tts
engines/openai-tts-cli.py  #对接openai-tts
assets/ # 参考音色文件夹，采用“配对命名法”，将参考音频与对应文本以相同文件名存储（如 warm_female.mp3 与 warm_female.txt），设计逻辑：qwen3-tts.py 在启动时自动扫描 assets 文件夹。
SKILL.md # tts-skill使用方法
README.md # tts-skill技能说明文件
```

**智能路由**：如果用户输入英文，系统自动锁定 `assets/en/` 路径下的参考音频，确保韵律和发音的准确性。

## 功能设计

### SKILL.md

- 需包含qwen3-tts安装方法、*-tts-cli.py的调用方法
- 定义“模糊语义”指令，“用户自然语言输入要求，即可完成音频文件生成”。

-  **指令模式**：`/tts-skill qwen3-tts [文本内容] --voice [音色关键词]`

- **语义对齐**：在 `SKILL.md`​ 的技能描述中注明： *“支持通过 assets 下的文件名前缀选择音色”* 。

- **交互逻辑**：当用户说“用赵信的声音读这段话”，AI 自动匹配到 `assets/赵信.mp3`。
- 当用户输入/tts-skill后，显示使用说明和使用方法。用户自然语言输入要求，即可完成音频文件生成。

#### qwen3-tts安装方法

```yaml
0. 检测用户是否有qwen3-tts虚拟环境：micromamba activate qwen3-tts，如果执行成功跳过1-8步骤。
1. 检测用户是否安装了python，没有进行安装
2. 检测用户是否安装了Micromamba，没有进行安装，Windows可使用：Invoke-Expression ((Invoke-WebRequest -Uri https://micro.mamba.pm/install.ps1 -UseBasicParsing).Content)
3. 创建 Qwen3-TTS 专用环境：micromamba create -n qwen3-tts python=3.12 -y
4. 激活python虚拟环境：micromamba activate qwen3-tts
5. 安装 Qwen3-TTS 核心包：pip install -U qwen-tts
6. 可选，安装 FlashAttention 2，可以显著减少 GPU 内存使用，提高推理效率，对于低配电脑使用CPU就好了。pip install -U flash-attn --no-build-isolation
7. 安装 modelscope ：pip install -U modelscope
8. Qwen3-TTS-12Hz-0.6B-Base模型下载：modelscope download --model Qwen/Qwen3-TTS-12Hz-0.6B-Base --local_dir ./Qwen3-TTS-12Hz-0.6B-Base
9. 调用qwen3-tts-cli.py

```

### qwen3_tts.py

- **默认态**：若用户未指定音色，脚本默认指向 `assets/赵信.mp3`。
- 编写edge-tts-cli.py，用书输入 /tts-skill 使用千问赵信音色，朗读文字[xxx]，即可克隆赵信音色，生成[xxx]的音频。
- 输入参数为：参考音频及对应参考文本（默认为assets/赵信[.mp](http://default.mp)3、assets/default.txt；要转换为音频的文本内容或文本文件（txt）；输出文件路径（默认为当前文件夹）。

### edge-tts-cli.py

- 编写edge-tts-cli.py，用书输入 /tts-skill 使用微软晓晓，朗读文字[xxx]，即可调zh-CN-XiaoxiaoNeural生成[xxx]的音频。
- 参考reference\VoiceCraft\README.md，理解如何使用
- 在SKILL.md中，给出edge-tts-cli.py可用的音色列表、支持的语音风格，参考reference\VoiceCraft\README.md
- 在edge-tts.config中设置用户的接口地址（默认为https://tts.wangwangit.com/v1/audio/speech）、音色（默认zh-CN-XiaoxiaoNeural）、语速（默认1）、语调（默认0）、风格（默认为general）

‍

‍

‍

‍
