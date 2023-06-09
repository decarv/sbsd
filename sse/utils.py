"""
TODO:
    - decide how to work with video data in Python more efficiently (this would potentially change load_data and
    save_data)


"""

import os
import sys
import random
import pickle
import requests
import srt
from moviepy import editor


def download_video(url: str, fp_out: str, headers=None) -> None:
    response = requests.get(url, stream=True, headers=headers)
    try:
        response.raise_for_status()
    except Exception as ex:  # TODO(decarv): catch specific exceptions
        print(ex)

    with open(fp_out, "wb") as f:
        for chunk in response.iter_content(chunk_size=int(5e+6)):
            f.write(chunk)


def download_subtitles(url: str, fp_out: str, headers=None) -> None:
    response = requests.get(url, stream=True, headers=headers)
    try:
        response.raise_for_status()
    except Exception as ex:  # TODO(decarv): catch specific exceptions
        print(ex)

    with open(fp_out, "wb") as f:
        f.write(response.content)


def save_video(filepath, data):
    if os.path.exists(filepath):
        ans = input(f"Do you wish to overwrite {filepath} [Y/n]?")
        if ans == 'Y':
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
    else:
        with open(filepath, "wb") as f:
            pickle.dump(data, f)


def load_video(filepath: str):
    with open(filepath, "rb") as f:
        return pickle.load(f)
    

def concatenate_videos(video_filenames, output_filename):
    clips = []

    # Load video files as clips
    for filename in video_filenames:
        clip = editor.VideoFileClip(filename)
        clips.append(clip)

    # Concatenate clips
    final_clip = editor.concatenate_videoclips(clips)

    # Write the output video file
    final_clip.write_videofile(output_filename, codec='libx264')
    

def concatenate_srt_files(input_files, output_file):
    all_subtitles = []
    time_offset = 0

    for input_file in input_files:
        with open(input_file, 'r', encoding='utf-8') as f:
            subtitles = list(srt.parse(f.read()))

        if len(all_subtitles) > 0:
            last_subtitle = all_subtitles[-1]
            time_offset = last_subtitle.end.total_seconds() + 4.1 # magic gap

        for subtitle in subtitles:
            subtitle.start += srt.timedelta(seconds=time_offset)
            subtitle.end += srt.timedelta(seconds=time_offset)
        print(subtitles[0])

        all_subtitles.extend(subtitles)

    with open(output_file, 'w', encoding='utf-8') as output_f:
        output_f.write(srt.compose(all_subtitles))