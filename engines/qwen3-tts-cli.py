#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-TTS CLI Engine
对接千问TTS模型，支持音色克隆和语音生成
"""

import os
import sys
import argparse
import subprocess
import json
import time
import threading
from pathlib import Path
import re

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

def detect_language(text):
    """检测文本语言，智能选择参考音频路径"""
    # 检测中文字符
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    # 检测英文字符
    english_pattern = re.compile(r'[a-zA-Z]')

    chinese_count = len(chinese_pattern.findall(text))
    english_count = len(english_pattern.findall(text))

    if chinese_count > english_count:
        return 'zh'
    else:
        return 'en'

def find_voice_reference(voice_keyword, language='zh'):
    """根据关键词在assets目录中查找匹配的参考音频"""
    assets_dir = Path(__file__).parent.parent / 'assets'

    if not assets_dir.exists():
        return None, None

    # 支持的音频格式
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac']

    # 搜索匹配的音频文件
    for audio_file in assets_dir.iterdir():
        if audio_file.suffix.lower() in audio_extensions:
            # 检查文件名是否包含关键词
            if voice_keyword.lower() in audio_file.stem.lower():
                # 查找对应的文本文件
                text_file = audio_file.with_suffix('.txt')
                if text_file.exists():
                    return str(audio_file), str(text_file)

    # 如果没有找到匹配的，返回默认的赵信音色
    default_text = assets_dir / '赵信.txt'
    if default_text.exists():
        for ext in audio_extensions:
            default_audio = assets_dir / f'赵信{ext}'
            if default_audio.exists():
                return str(default_audio), str(default_text)

    # 如果连默认文件都不存在，返回第一个找到的音频文件
    for audio_file in assets_dir.iterdir():
        if audio_file.suffix.lower() in audio_extensions:
            text_file = audio_file.with_suffix('.txt')
            if text_file.exists():
                return str(audio_file), str(text_file)

    return None, None

def check_qwen3_environment():
    """检查Qwen3-TTS环境是否已配置"""
    try:
        # 检查是否在qwen3-tts虚拟环境中
        result = subprocess.run(['micromamba', 'run', '-n', 'qwen3-tts', 'python', '-c', 'import qwen_tts'],
                              capture_output=True, text=True)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_qwen3_environment():
    """安装Qwen3-TTS环境"""
    print("正在配置Qwen3-TTS环境...")

    try:
        # 1. 检查Python
        python_check = subprocess.run(['python', '--version'], capture_output=True, text=True)
        if python_check.returncode != 0:
            print("❌ Python未安装，请先安装Python 3.12或更高版本")
            return False

        # 2. 检查Micromamba
        try:
            subprocess.run(['micromamba', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("正在安装Micromamba...")
            if os.name == 'nt':  # Windows
                ps_command = "Invoke-Expression ((Invoke-WebRequest -Uri https://micro.mamba.pm/install.ps1 -UseBasicParsing).Content)"
                subprocess.run(['powershell', '-Command', ps_command], check=True)
            else:  # Linux/Mac
                subprocess.run(['curl', '-Ls', 'https://micro.mamba.pm/install.sh'],
                             stdout=subprocess.PIPE, check=True)

        # 3. 创建虚拟环境
        print("正在创建qwen3-tts虚拟环境...")
        subprocess.run(['micromamba', 'create', '-n', 'qwen3-tts', 'python=3.12', '-y'], check=True)

        # 4. 安装Qwen-TTS包
        print("正在安装Qwen3-TTS核心包...")
        subprocess.run(['micromamba', 'run', '-n', 'qwen3-tts', 'pip', 'install', '-U', 'qwen-tts'], check=True)

        # 5. 安装modelscope
        print("正在安装modelscope...")
        subprocess.run(['micromamba', 'run', '-n', 'qwen3-tts', 'pip', 'install', '-U', 'modelscope'], check=True)

        print("✅ Qwen3-TTS环境配置完成！")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 环境配置失败: {e}")
        return False

def generate_speech_qwen3(reference_audio, reference_text, text, output_path):
    """使用Qwen3-TTS生成语音"""
    try:
        # 创建临时Python脚本文件
        temp_script = Path(__file__).parent / 'temp_qwen3_generate.py'

        script_content = '''import sys
import os
import torch
import time
import threading
from pathlib import Path

# 添加当前目录到路径
sys.path.append(".")

# 设置UTF-8编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

try:
    # 导入必要的库
    print("📥 加载必要的库...")
    from qwen_tts import Qwen3TTSModel
    from modelscope import snapshot_download
    import torchaudio
    import numpy as np
    from tqdm import tqdm
    import soundfile as sf

    # 记录开始时间
    start_time = time.time()
    generation_start = time.time()

    print("⏰ 开始时间: " + time.strftime('%Y-%m-%d %H:%M:%S'))
    print("📝 输入文本: ''' + text + ''' (" + str(len(''' + repr(text) + ''')) + " 字)")
    print("🎵 参考音频: " + os.path.basename(''' + repr(reference_audio) + ''') + "...")

    # 下载模型（如果未下载）
    print("\\n📥 下载/加载 Qwen3-TTS 模型...")
    try:
        model_dir = snapshot_download('Qwen/Qwen3-TTS-12Hz-0.6B-Base', local_dir='./Qwen3-TTS-12Hz-0.6B-Base')
    except Exception as e:
        print("模型下载警告: " + str(e))
        model_dir = './Qwen3-TTS-12Hz-0.6B-Base'

    # 初始化模型
    print("🔧 初始化模型...")
    tts = Qwen3TTSModel.from_pretrained(model_dir)

    # 读取参考文本
    print("📖 读取参考文本...")
    ref_text_path = ''' + repr(reference_text) + '''
    with open(ref_text_path, 'r', encoding='utf-8') as f:
        ref_text = f.read().strip()

    # 进度跟踪变量
    progress_status = {'progress': 0, 'stop_progress': False}

    # 创建进度条和预计完成时间显示
    print("\\n🎵 正在生成语音...")
    progress_bar = tqdm(
        total=100,
        desc="语音生成进度",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_noinv_fmt}]",
        ncols=80
    )

    def update_progress():
        """更新进度条的后台线程"""
        while not progress_status['stop_progress'] and progress_status['progress'] < 100:
            elapsed = time.time() - generation_start
            # 基于文本长度估算进度（假设每字需要一定时间）
            estimated_total_time = ''' + str(len(text)) + ''' * 0.5  # 假设每字0.5秒
            progress_status['progress'] = min(99, int((elapsed / estimated_total_time) * 100))

            progress_text = "语音生成进度 (" + str(progress_status['progress']) + "%)"
            progress_bar.set_description(progress_text)

            progress_bar.update(max(0, progress_status['progress'] - progress_bar.n))
            time.sleep(0.5)

        # 完成时更新到100%
        if progress_status['progress'] < 100:
            progress_bar.update(100 - progress_bar.n)
        progress_bar.close()

    # 启动进度条线程
    progress_thread = threading.Thread(target=update_progress)
    progress_thread.start()

    # 生成语音
    ref_audio_path = ''' + repr(reference_audio) + '''
    result = tts.generate_voice_clone(
        text=''' + repr(text) + ''',
        ref_audio=ref_audio_path,
        ref_text=ref_text,
        x_vector_only_mode=False
    )

    # 处理不同的返回格式
    if isinstance(result, tuple) and len(result) == 2:
        wavs, sample_rate = result
    else:
        # 如果只返回音频数据，使用默认采样率
        wavs = result
        sample_rate = 22050  # 默认采样率

    # 停止进度条
    progress_status['stop_progress'] = True
    progress_thread.join()

    # 记录生成结束时间
    generation_end = time.time()
    generation_time = generation_end - generation_start

    # 保存结果
    output_path = ''' + repr(output_path) + '''
    sf.write(str(output_path), wavs[0], sample_rate)

    # 计算统计信息
    total_time = time.time() - start_time
    text_length = ''' + str(len(text)) + '''
    time_per_char = generation_time / text_length if text_length > 0 else 0

    # 输出结果
    print("\\n✅ 语音生成成功!")
    print("📁 输出文件: " + str(output_path))
    print("🎵 采样率: " + str(sample_rate) + " Hz")
    print("⏱️  音频长度: " + str(len(wavs[0]) / sample_rate) + " 秒")

    print("\\n📊 性能统计:")
    print("   总用时: " + str(total_time/60) + " 分钟 (" + str(total_time) + " 秒)")
    print("   生成用时: " + str(generation_time/60) + " 分钟 (" + str(generation_time) + " 秒)")
    print("   文本长度: " + str(text_length) + " 字")
    print("   平均每字用时: " + str(time_per_char) + " 秒")

except Exception as e:
    # 确保进度条被正确关闭
    if 'progress_status' in locals():
        progress_status['stop_progress'] = True
        if 'progress_thread' in locals():
            progress_thread.join()
        if 'progress_bar' in locals():
            progress_bar.close()

    print("\\n❌ 错误: " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

        # 写入临时文件
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 执行Python脚本
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        env['PYTHONUNBUFFERED'] = '1'

        cmd = ['micromamba', 'run', '-n', 'qwen3-tts', 'python', str(temp_script)]
        result = subprocess.run(cmd, env=env, cwd=os.getcwd())
        return_code = result.returncode

        # 清理临时文件
        try:
            os.remove(temp_script)
        except:
            pass

        if return_code == 0:
            return True, output_path
        else:
            return False, f"生成失败 (exit={return_code})"

    except Exception as e:
        return False, f"执行错误: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Qwen3-TTS CLI - 千问TTS语音生成工具')
    parser.add_argument('text', nargs='?', help='要转换为语音的文本内容')
    parser.add_argument('--voice', '-v', default='赵信', help='音色关键词（默认：赵信）')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--text-file', '-f', help='从文本文件读取内容')
    parser.add_argument('--install', action='store_true', help='安装Qwen3-TTS环境')
    parser.add_argument('--list-voices', action='store_true', help='列出可用的音色')

    args = parser.parse_args()

    if args.install:
        install_qwen3_environment()
        return

    if args.list_voices:
        assets_dir = Path(__file__).parent.parent / 'assets'
        print("可用的音色:")
        if not assets_dir.exists():
            return

        audio_extensions = {'.mp3', '.wav', '.m4a', '.flac'}
        stems = set()
        for audio_file in assets_dir.iterdir():
            if audio_file.suffix.lower() in audio_extensions:
                stems.add(audio_file.stem)

        for stem in sorted(stems):
            print(f"  - {stem}")
        return

    # 获取文本内容
    text = ""
    if args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    elif args.text:
        text = args.text
    else:
        print("ERROR: 请提供文本内容或文本文件")
        parser.print_help()
        return

    if not text:
        print("ERROR: 文本内容不能为空")
        return

    # 检测语言并查找音色
    language = detect_language(text)
    reference_audio, reference_text = find_voice_reference(args.voice, language)

    if not reference_audio or not reference_text:
        print(f"ERROR: 找不到匹配的音色文件: {args.voice}")
        return

    print(f"使用音色: {Path(reference_audio).stem}")
    print(f"文本内容: {text[:50]}{'...' if len(text) > 50 else ''}")

    # 设置输出路径
    if not args.output:
        # 生成默认文件名：日期+文本前6个字
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        prefix = text[:6] if len(text) >= 6 else text
        prefix = "".join(c for c in prefix if c.isalnum() or c in "_-")
        filename = f"{timestamp}_{prefix}.wav"

        # 默认输出到上级目录的output文件夹
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / filename
    else:
        output_path = args.output

    # 检查环境
    if not check_qwen3_environment():
        print("WARNING: Qwen3-TTS环境未配置，正在安装...")
        if not install_qwen3_environment():
            print("ERROR: 环境配置失败，请手动配置")
            return

    # 生成语音
    success, result = generate_speech_qwen3(reference_audio, reference_text, text, output_path)

    if success:
        print(f"SUCCESS: 语音生成成功: {result}")
    else:
        # Handle Unicode characters in error message
        try:
            print(f"ERROR: 生成失败: {result}")
        except UnicodeEncodeError:
            # Fallback: encode with error handling
            safe_result = result.encode('gbk', errors='replace').decode('gbk')
            print(f"ERROR: 生成失败: {safe_result}")

if __name__ == '__main__':
    main()
