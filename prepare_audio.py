from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import random
import subprocess
import sys

import av
import imageio_ffmpeg

ROOT = Path(__file__).parent
SOURCE = ROOT / "song_list"
OUTPUT = SOURCE / "web_audio"
TRACKS = [
    ("如果可以", "韦礼安-如果可以.flac"),
    ("红尘客栈", "周杰伦-红尘客栈.flac"),
    ("几分之几", "卢广仲-几分之几.flac"),
    ("一样的月光", "徐佳莹-一样的月光.mkv"),
    ("特别的人", "方大同-特别的人.mkv"),
    ("紧急联系人", "Gareth.T-紧急联络人.mkv"),
    ("红豆", "王菲-红豆.mkv"),
    ("我怀念的", "孙燕姿-我怀念的.mkv"),
    ("爱爱爱", "方大同-爱爱爱.mkv"),
    ("蝴蝶", "陶喆-蝴蝶.mkv"),
    ("修炼爱情", "林俊杰-修炼爱情.mkv"),
    ("暖暖", "梁静茹-暖暖.mkv"),
    ("一半一半", "Top Barry&INDEcompany-一半一半.mkv"),
    ("水星记", "郭顶-水星记.mkv"),
    ("幻听", "许嵩-幻听.mkv"),
    ("刻在我心底的名字", "卢广仲-刻在我心底的名字.mkv"),
    ("当你", "王心凌-当你.mkv"),
    ("才二十三", "方大同-才二十三.mkv"),
    ("小镇姑娘", "陶喆-小镇姑娘.mkv"),
    ("最佳损友", "陈奕迅-最佳损友.mkv"),
]

def convert(item):
    index, (title, filename) = item
    source = SOURCE / filename
    if not source.is_file():
        raise FileNotFoundError(f"Missing source for track {index:02}: {filename}")
    container = av.open(str(source))
    duration = float(container.duration / av.time_base) if container.duration else 0
    has_audio = any(stream.type == "audio" for stream in container.streams)
    container.close()
    if not has_audio or duration <= 0:
        raise RuntimeError(f"No audio stream or duration: track {index:02}")
    clip_length = min(30.0, duration)
    max_start = max(0.0, duration - clip_length)
    rng = random.Random(20261031 + index)
    start = rng.uniform(max_start * 0.15, max_start * 0.85) if max_start else 0.0
    output = OUTPUT / f"{index:02}.mp3"
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.3f}", "-i", str(source), "-map", "0:a:0", "-vn",
        "-t", f"{clip_length:.3f}", "-ac", "2", "-ar", "44100", "-b:a", "128k",
        "-metadata", f"title={title}", str(output),
    ]
    subprocess.run(command, check=True, capture_output=True)
    return f"{index:02} {title}: {clip_length:.1f}s"

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(convert, item) for item in enumerate(TRACKS, start=1)]
        for future in as_completed(futures):
            print(future.result(), flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise
