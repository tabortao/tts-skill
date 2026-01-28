#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-TTS 最终测试脚本
使用指定的输入输出路径和格式
"""

import os
import torch
import soundfile as sf
import time
from pathlib import Path
import threading
from tqdm import tqdm

def load_reference_data():
    """加载参考音频和文本"""
    ref_audio_path = "Inputs/Reference Audio/ReferenceAudio.wav"
    ref_text_path = "Inputs/Reference Audio/ReferenceAudio.txt"
    input_text_path = "Inputs/Input_text.txt"

    # 检查文件是否存在
    missing_files = []
    for file_path in [ref_audio_path, ref_text_path, input_text_path]:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("❌ 缺少必要的输入文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return None, None, None

    # 加载参考文本
    with open(ref_text_path, 'r', encoding='utf-8') as f:
        ref_text = f.read().strip()

    # 加载输入文本
    with open(input_text_path, 'r', encoding='utf-8') as f:
        input_text = f.read().strip()

    print(f"✅ 参考音频: {ref_audio_path}")
    print(f"✅ 参考文本: {ref_text[:50]}...")
    print(f"✅ 输入文本: {input_text[:50]}...")

    return ref_audio_path, ref_text, input_text

def generate_output_filename(input_text):
    """生成输出文件名"""
    # 获取当前时间
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # 获取输入文本的前6个字
    prefix = input_text[:6] if len(input_text) >= 6 else input_text
    # 清理文件名，移除不合法的字符
    prefix = "".join(c for c in prefix if c.isalnum() or c in "_-")

    return f"{timestamp}_{prefix}.wav"

def test_qwen3_tts():
    """主测试函数"""
    print("🤖 Qwen3-TTS 语音克隆测试")
    print("=" * 60)

    # 记录开始时间
    start_time = time.time()
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 加载输入数据
    print("\n📂 加载输入数据...")
    ref_audio_path, ref_text, input_text = load_reference_data()

    if not ref_audio_path:
        return False

    # 2. 创建输出目录
    output_dir = Path("Outputs")
    output_dir.mkdir(exist_ok=True)
    print(f"✅ 输出目录: {output_dir}")

    try:
        # 3. 加载模型
        print("\n📥 加载 Qwen3-TTS 模型...")
        from qwen_tts import Qwen3TTSModel

        model_path = "./Qwen3-TTS-12Hz-0.6B-Base"
        model = Qwen3TTSModel.from_pretrained(
            model_path,
            device_map="cpu",
            dtype=torch.float32,
        )
        print("✅ 模型加载成功!")

        # 4. 执行语音克隆
        print(f"\n🎵 正在生成语音...")
        print(f"   输入文本: {input_text}")
        print(f"   参考音频: {ref_audio_path}")

        # 记录生成开始时间
        generation_start = time.time()

        # 创建进度条和预计完成时间显示
        progress_bar = tqdm(
            total=100,
            desc="语音生成进度",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_noinv_fmt}]",
            ncols=80
        )

        # 进度跟踪变量
        progress = 0
        stop_progress = False

        def update_progress():
            """更新进度条的后台线程"""
            nonlocal progress, stop_progress
            while not stop_progress and progress < 100:
                elapsed = time.time() - generation_start
                # 基于文本长度估算进度（假设每字需要一定时间）
                estimated_total_time = len(input_text) * 0.5  # 假设每字0.5秒
                progress = min(99, int((elapsed / estimated_total_time) * 100))

                if progress > 0 and elapsed > 0:
                    eta = (elapsed / progress) * (100 - progress)
                    progress_bar.set_description(f"语音生成进度 (ETA: {eta:.1f}s)")

                progress_bar.update(max(0, progress - progress_bar.n))
                time.sleep(0.5)

            # 完成时更新到100%
            if progress < 100:
                progress_bar.update(100 - progress_bar.n)
            progress_bar.close()

        # 启动进度条线程
        progress_thread = threading.Thread(target=update_progress)
        progress_thread.start()

        wavs, sample_rate = model.generate_voice_clone(
            text=input_text,
            language="Chinese",  # 根据输入文本自动判断
            ref_audio=ref_audio_path,
            ref_text=ref_text,
        )

        # 停止进度条
        stop_progress = True
        progress_thread.join()

        # 记录生成结束时间
        generation_end = time.time()
        generation_time = generation_end - generation_start

        # 5. 保存结果
        output_filename = generate_output_filename(input_text)
        output_path = output_dir / output_filename

        sf.write(str(output_path), wavs[0], sample_rate)

        # 6. 计算统计信息
        total_time = time.time() - start_time
        text_length = len(input_text)
        time_per_char = generation_time / text_length if text_length > 0 else 0

        # 7. 输出结果
        print(f"\n✅ 语音生成成功!")
        print(f"📁 输出文件: {output_path}")
        print(f"🎵 采样率: {sample_rate} Hz")
        print(f"⏱️  音频长度: {len(wavs[0]) / sample_rate:.2f} 秒")

        print(f"\n📊 性能统计:")
        print(f"   总用时: {total_time/60:.2f} 分钟 ({total_time:.2f} 秒)")
        print(f"   生成用时: {generation_time/60:.2f} 分钟 ({generation_time:.2f} 秒)")
        print(f"   文本长度: {text_length} 字")
        print(f"   平均每字用时: {time_per_char:.4f} 秒")

        return True

    except Exception as e:
        # 确保进度条被正确关闭
        if 'stop_progress' in locals():
            stop_progress = True
            if 'progress_thread' in locals():
                progress_thread.join()
            if 'progress_bar' in locals():
                progress_bar.close()

        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_qwen3_tts()

    print("\n" + "=" * 60)
    if success:
        print("🎉 测试完成！语音克隆成功！")
    else:
        print("❌ 测试失败，请检查错误信息")
        print("\n💡 故障排除:")
        print("   1. 检查输入文件路径是否正确")
        print("   2. 确认模型文件夹存在")
        print("   3. 检查文件权限")
    print("=" * 60)

if __name__ == "__main__":
    main()