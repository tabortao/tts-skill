import sys
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
    print("📝 输入文本: 你好，我是中国人。 (" + str(len('你好，我是中国人。')) + " 字)")
    print("🎵 参考音频: " + os.path.basename('F:\\Code\\MySkills\\tts-skill\\assets\\寒冰射手.mp3') + "...")

    # 下载模型（如果未下载）
    print("\n📥 下载/加载 Qwen3-TTS 模型...")
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
    ref_text_path = 'F:\\Code\\MySkills\\tts-skill\\assets\\寒冰射手.txt'
    with open(ref_text_path, 'r', encoding='utf-8') as f:
        ref_text = f.read().strip()

    # 进度跟踪变量
    progress_status = {'progress': 0, 'stop_progress': False}

    # 创建进度条和预计完成时间显示
    print("\n🎵 正在生成语音...")
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
            estimated_total_time = 9 * 0.5  # 假设每字0.5秒
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
    ref_audio_path = 'F:\\Code\\MySkills\\tts-skill\\assets\\寒冰射手.mp3'
    result = tts.generate_voice_clone(
        text='你好，我是中国人。',
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
    output_path = 'F:\\Code\\MySkills\\tts-skill\\output\\20260128_180805_你好，我是中.wav'
    sf.write(str(output_path), wavs[0], sample_rate)

    # 计算统计信息
    total_time = time.time() - start_time
    text_length = 9
    time_per_char = generation_time / text_length if text_length > 0 else 0

    # 输出结果
    print("\n✅ 语音生成成功!")
    print("📁 输出文件: " + str(output_path))
    print("🎵 采样率: " + str(sample_rate) + " Hz")
    print("⏱️  音频长度: " + str(len(wavs[0]) / sample_rate) + " 秒")

    print("\n📊 性能统计:")
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

    print("\n❌ 错误: " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
