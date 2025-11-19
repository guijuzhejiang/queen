#!/usr/bin/env python3
"""
extract_multi_downscale.py

用法:
    python extract_multi_downscale.py /path/to/video_dir -n 4

说明:
 - 脚本会遍历指定目录下的所有常见视频文件（仅当前目录，不递归）。
 - 每个视频生成目录: <video_stem>/images ，例如 cam08.mp4 -> cam08/images/
 - 每帧以 PNG 保存，文件名 frame_000000.png、frame_000001.png ...
 - 每帧宽高缩小 2 倍（scale=0.5）
 - 使用多进程同时处理多个视频，进程数由 -n 指定
 - 新增参数 --max-frames (-m) 控制每个视频最多保存多少帧（默认 300，<=0 表示不限制）
"""

import os
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple, Union
import multiprocessing
import traceback
from PIL import Image

VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.MP4', '.MOV', '.AVI', '.MKV'}
DEFAULT_MAX_FRAMES = 300


def find_videos_in_dir(dirpath: Path) -> List[Path]:
    """列出目录下的视频文件（非递归）"""
    vids = []
    if not dirpath.is_dir():
        return vids
    for p in sorted(dirpath.iterdir()):
        if p.is_file() and p.suffix in VIDEO_EXTS:
            vids.append(p)
    return vids


def process_video(video_path_input: Union[str, Tuple[str, int]]) -> Tuple[str, bool, str, int]:
    """
    在子进程中执行：抽取并缩小 2 倍保存帧为 PNG。
    参数 video_path_input 可以是字符串（视频路径），也可以是 (video_path_str, max_frames)
    返回 (video_path, success, message, frames_saved)
    """
    import cv2  # 在子进程内导入
    if isinstance(video_path_input, (list, tuple)):
        video_path_str, max_frames = video_path_input[0], int(video_path_input[1])
    else:
        video_path_str = video_path_input
        max_frames = DEFAULT_MAX_FRAMES

    video_path = Path(video_path_str)
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return (str(video_path), False, "无法打开视频文件", 0)

        orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or None
        orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or None
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.get(cv2.CAP_PROP_FRAME_COUNT) > 0 else None

        # 输出目录: <parent>/<video_stem>/images
        out_base = video_path.with_suffix('')  # same name without extension, in same folder
        out_dir = out_base / "images"
        out_dir.mkdir(parents=True, exist_ok=True)

        # 缩小 2 倍（宽高各 /2）
        if orig_w is None or orig_h is None or orig_w <= 0 or orig_h <= 0:
            # 若无法读取宽高，先读取第一帧来获知
            success, frame = cap.read()
            if not success:
                cap.release()
                return (str(video_path), False, "无法读取视频首帧以确定分辨率", 0)
            orig_h, orig_w = frame.shape[0], frame.shape[1]
            # 把指针复位
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        new_w = max(1, orig_w // 2)
        new_h = max(1, orig_h // 2)

        # 处理 max_frames 参数：<=0 表示不限制
        max_frames_to_save = None if (max_frames is None or int(max_frames) <= 0) else int(max_frames)

        frame_idx = 0
        success, frame = cap.read()
        while success and (max_frames_to_save is None or frame_idx < max_frames_to_save):
            # 使用 INTER_AREA 缩小更好
            try:
                resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
            except Exception:
                # 如果 resize 出错，直接跳过该帧（保存原帧）
                resized = frame

            out_path = out_dir / f"{frame_idx:04d}.png"
            # cv2.imwrite 返回 bool 表示是否成功
            write_ok = cv2.imwrite(str(out_path), resized)
            if not write_ok:
                cap.release()
                return (str(video_path), False, f"写入失败: {out_path}", frame_idx)

            frame_idx += 1
            success, frame = cap.read()

        cap.release()
        # 组成返回信息，若被限制则说明
        if max_frames_to_save is not None and total_frames is not None and total_frames > max_frames_to_save:
            msg = f"完成，保存 {frame_idx} 帧 到 {out_dir} (缩放至 {new_w}x{new_h})，已限制为最多 {max_frames_to_save} 帧（视频共有 {total_frames} 帧）"
        elif max_frames_to_save is not None and total_frames is None:
            msg = f"完成，保存 {frame_idx} 帧 到 {out_dir} (缩放至 {new_w}x{new_h})，已限制为最多 {max_frames_to_save} 帧"
        else:
            msg = f"完成，保存 {frame_idx} 帧 到 {out_dir} (缩放至 {new_w}x{new_h})"
        return (str(video_path), True, msg, frame_idx)
    except Exception as e:
        tb = traceback.format_exc()
        return (str(video_path), False, f"异常: {e}\n{tb}", 0)


def main():
    parser = ArgumentParser(description="从目录中批量抽帧并缩小 2 倍（每个视频保存到 <video_stem>/images，PNG 格式）")
    parser.add_argument("--datadir", default='/home/zzg/data/CV/dynerf/Take_154814_ud',
                        help="包含视频文件的目录（只遍历该目录，不递归）")
    parser.add_argument("-n", "--num-processes", type=int, default=10,
                        help="并行处理视频的进程数（默认: CPU 核心数）")
    parser.add_argument("-m", "--max-frames", type=int, default=DEFAULT_MAX_FRAMES,
                        help="每个视频最多抽取多少帧，设置为 <=0 表示不限制（默认: 300）")
    args = parser.parse_args()

    video_dir = Path(args.datadir)
    if not video_dir.exists() or not video_dir.is_dir():
        parser.error(f"目录不存在或不是文件夹: {video_dir}")

    vids = find_videos_in_dir(video_dir)
    if not vids:
        print(f"在目录 {video_dir} 未发现支持的视频文件（扩展名 {sorted(VIDEO_EXTS)}）")
        return

    n = max(1, args.num_processes)
    print(f"发现 {len(vids)} 个视频，将使用 {n} 个进程并行处理。每个视频最多保存 {args.max_frames} 帧（<=0 表示不限制）。")

    # 使用 multiprocessing.Pool 并行处理视频（传入 (path, max_frames) 以便子进程知晓上限）
    video_inputs = [(str(p), args.max_frames) for p in vids]
    results = []
    if n == 1:
        # 单进程直接顺序执行，便于调试
        for vi in video_inputs:
            res = process_video(vi)
            results.append(res)
            print(f"[{Path(res[0]).name}] -> {'OK' if res[1] else 'ERR'}: {res[2]}")
    else:
        # 并行
        with multiprocessing.Pool(processes=n) as pool:
            for res in pool.imap_unordered(process_video, video_inputs):
                results.append(res)
                vp, ok, msg, frames = res
                name = Path(vp).name
                status = "OK" if ok else "ERR"
                print(f"[{name}] -> {status}: {msg}")

    # 汇总
    ok_count = sum(1 for r in results if r[1])
    err_count = len(results) - ok_count
    total_frames = sum(r[3] for r in results)
    print("======================================")
    print(f"任务完成: {len(results)} 个视频, 成功 {ok_count}, 失败 {err_count}, 共保存 {total_frames} 帧")
    if err_count > 0:
        print("出现错误的视频：")
        for r in results:
            if not r[1]:
                print(f" - {Path(r[0]).name}: {r[2]}")
    print("======================================")


if __name__ == "__main__":
    main()
