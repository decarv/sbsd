import pickle
import cv2
import random
import os


def extract_random_frames(video_file, start_time, end_time, output_file, num_frames=1):
    video = cv2.VideoCapture(video_file)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    if start_frame >= end_frame:
        start_frame = end_frame-1
    random_frames = random.sample(range(start_frame, end_frame), num_frames)
    frame_count = 0
    for frame_number in sorted(random_frames):
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = video.read()

        if ret:
            cv2.imwrite(output_file, frame)
            frame_count += 1

    # Release the video object
    video.release()
    return frame


def sample_frames(clips_num, clips_dir, data, data_dir, frame_dir):
    frames = [[] for _ in range(clips_num)]

    for clip_num in range(clips_num):
        filename = os.path.join(clips_dir, f"clip_{clip_num}.mp4")
        company, description, subtitles = data[clip_num]
        if len(subtitles) == 0:
            continue
        for j, (start, end, subtitle) in enumerate(subtitles):
            print("Sampling: ", j, start, end, subtitle)
            frame = extract_random_frames(filename, start, end,
                                          os.path.join(data_dir, frame_dir, f"{clip_num}_{j}.png"))
            frames[clip_num].append(frame)

