import pyttsx3
import re
import os
import subprocess
from pathlib import Path

# ===================== 配置区 =====================
TEXT_CONTENT = """
在这里粘贴你的长文本。
Windows自带离线语音合成，不需要下载任何模型。
没有网络请求，不存在403错误。
适合旁白朗读配音。
"""

# 语速，默认200，越小越慢，推荐140~190
RATE = 160
VOLUME = 0.9
OUTPUT_WAV = "tts_total.wav"
OUTPUT_MP3 = "tts_total.mp3"
TMP_FOLDER = "./tmp_tts_wavs"
# =================================================

def split_long_text(text: str, max_len=80):
    sentences = re.split(r'([。！？])', text.strip())
    seg_list = []
    buf = ""
    for sent in sentences:
        buf += sent
        if len(buf) >= max_len:
            seg = buf.strip()
            if seg:
                seg_list.append(seg)
            buf = ""
    seg = buf.strip()
    if seg:
        seg_list.append(seg)
    return seg_list

def wav_to_mp3(wav_path, mp3_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", wav_path,
        "-acodec", "libmp3lame",
        "-b:a", "128k",
        mp3_path
    ]
    subprocess.run(cmd, capture_output=True)

def merge_wav(input_wav_list, out_wav):
    concat_file = Path(TMP_FOLDER) / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for w in input_wav_list:
            f.write(f"file '{Path(w).absolute()}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c", "copy", out_wav
    ], capture_output=True)
    concat_file.unlink(missing_ok=True)

def main():
    os.makedirs(TMP_FOLDER, exist_ok=True)
    engine = pyttsx3.init()
    engine.setProperty('rate', RATE)
    engine.setProperty('volume', VOLUME)

    # 列出系统所有可用语音，找到中文女声晓晓 / 男声慧涛
    voices = engine.getProperty('voices')
    for i, v in enumerate(voices):
        print(f"{i}: {v.name} | {v.id}")
    # 👉 修改这里选择中文语音，复制上面打印出来的序号
    voice_idx = 0
    engine.setProperty('voice', voices[voice_idx].id)

    seg_list = split_long_text(TEXT_CONTENT, 80)
    print(f"一共 {len(seg_list)} 段")
    tmp_files = []
    for idx, seg in enumerate(seg_list):
        print(f"\n[{idx+1}/{len(seg_list)}] {seg}")
        tmp_wav = Path(TMP_FOLDER)/f"seg_{idx:04d}.wav"
        engine.save_to_file(seg, str(tmp_wav))
        engine.runAndWait()
        tmp_files.append(str(tmp_wav))

    merge_wav(tmp_files, OUTPUT_WAV)
    wav_to_mp3(OUTPUT_WAV, OUTPUT_MP3)
    print(f"\n✅ 输出：{OUTPUT_MP3}")

if __name__ == "__main__":
    main()
