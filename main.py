import cv2
import numpy as np
import subprocess
import os


def frame_to_time(frame, fps):
    """
    프레임을 시간(초)으로 변환
    :param frame: 프레임 번호
    :param fps: 초당 프레임 수 (Frames Per Second)
    :return: 초 (시간 단위)
    """
    return frame / fps


def extract_and_cut_audio(input_media, cut_ranges, fps, output_audio_directory):
    """
    MP4 파일에서 오디오를 추출하고, 프레임 구간에 맞춰 오디오를 자르는 함수
    :param input_media: 원본 MP4 파일 경로
    :param cut_ranges: (시작 프레임, 끝 프레임) 리스트
    :param fps: 프레임 속도 (Frames Per Second)
    :param output_audio_directory: 잘린 오디오 파일을 저장할 경로
    """
    if not os.path.exists(output_audio_directory):
        os.makedirs(output_audio_directory)

    for idx, (start_frame, end_frame) in enumerate(cut_ranges):
        # 프레임을 시간(초)으로 변환
        start_time = frame_to_time(start_frame, fps)
        end_time = frame_to_time(end_frame, fps)

        # 출력 파일명 생성
        output_audio = f"{output_audio_directory}/cut_audio_{idx + 1}.mp3"

        # FFmpeg 명령어 생성 및 실행 (mp4에서 오디오만 추출하여 잘라냄)
        command = [
            'ffmpeg', '-i', input_media, '-ss', str(start_time), '-to', str(end_time),
            '-q:a', '0', '-map', 'a', output_audio
        ]
        subprocess.run(command)


def cut_video(input_path, output_path, start_frame, end_frame):
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print(f"영상 파일을 열 수 없습니다: {input_path}")
        return False

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 시작 프레임으로 이동
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    current_frame = start_frame
    while current_frame <= end_frame and current_frame < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()
    print(f"영상이 성공적으로 저장되었습니다: {output_path}")
    return True


def merge_audio_video(cut_video_files, cut_audio_files, output_merged_directory):
    """
    잘린 영상과 잘린 오디오를 합쳐서 새로운 영상 파일을 생성하는 함수
    :param cut_video_files: 잘린 영상 파일들의 경로 리스트
    :param cut_audio_files: 잘린 오디오 파일들의 경로 리스트
    :param output_merged_directory: 합쳐진 영상 파일을 저장할 경로
    """
    if not os.path.exists(output_merged_directory):
        os.makedirs(output_merged_directory)

    for idx, (video_file, audio_file) in enumerate(zip(cut_video_files, cut_audio_files)):
        # 출력 파일명 생성
        output_merged_file = f"{output_merged_directory}/merged_video_{idx+1}.mp4"

        # FFmpeg 명령어 생성 및 실행 (영상과 오디오를 합침)
        command = [
            'ffmpeg', '-i', video_file, '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
            output_merged_file
        ]
        subprocess.run(command)


def merge_videos(input_paths, output_path):
    if not input_paths:
        print("합칠 영상 파일 목록이 비어 있습니다.")
        return False

    # 첫 번째 영상으로부터 영상 정보 가져오기
    cap = cv2.VideoCapture(input_paths[0])
    if not cap.isOpened():
        print(f"영상 파일을 열 수 없습니다: {input_paths[0]}")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    cap.release()

    # 모든 영상이 동일한 해상도와 FPS를 가지는지 확인
    for path in input_paths:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"영상 파일을 열 수 없습니다: {path}")
            return False
        current_fps = cap.get(cv2.CAP_PROP_FPS)
        current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if current_fps != fps or current_width != width or current_height != height:
            print(f"영상의 해상도 또는 FPS가 다릅니다: {path}")
            cap.release()
            out.release()
            return False
        cap.release()

    # 모든 영상을 순서대로 합치기
    for path in input_paths:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"영상 파일을 열 수 없습니다: {path}")
            continue
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        cap.release()
        print(f"영상이 성공적으로 합쳐졌습니다: {path}")

    out.release()
    print(f"모든 영상이 합쳐져서 저장되었습니다: {output_path}")
    return True


# 1. OpenCV로 영상의 해상도를 업스케일하는 과정
def upscale_video(input_video_path, output_video_path, scale_factor=2):
    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정
    fps = cap.get(cv2.CAP_PROP_FPS)  # 원본 영상의 FPS
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * scale_factor)  # 해상도 업스케일
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * scale_factor)

    # 영상을 저장할 객체 생성
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # 프레임을 업스케일
        upscaled_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_CUBIC)
        out.write(upscaled_frame)

    cap.release()
    out.release()


if __name__ == "__main__":

    input_media = 'videos/IMG_1153.MOV'
    fps = 30

    output_audio_directory = './output_audio'  # 잘린 오디오 파일을 저장할 폴더 경로
    output_video_directory = './output_video'  # 잘린 영상 파일을 저장할 폴더 경로
    output_merged_directory = './clips'  # 합쳐진 파일을 저장할 폴더 경로

    input_video = 'IMG_1153.MOV'
    cut_video1 = 'cut_video1.mp4'
    cut_video2 = 'cut_video2.mp4'
    cut_video3 = 'cut_video3.mp4'
    cut_video4 = 'cut_video4.mp4'
    cut_video5 = 'cut_video5.mp4'
    cut_video6 = 'cut_video6.mp4'
    cut_video7 = 'cut_video7.mp4'
    cut_video8 = 'cut_video8.mp4'
    cut_video9 = 'cut_video9.mp4'
    cut_video10 = 'cut_video10.mp4'
    cut_video11 = 'cut_video11.mp4'
    cut_video12 = 'cut_video12.mp4'
    cut_video13 = 'cut_video13.mp4'
    cut_video14 = 'cut_video14.mp4'
    cut_video15 = 'cut_video15.mp4'
    cut_video16 = 'cut_video16.mp4'
    cut_video17 = 'cut_video17.mp4'
    cut_video18 = 'cut_video18.mp4'

    # 원하는 프레임 범위 지정
    cut_ranges = [
        (2250, 2700),  # 박건 스루패스
        (4140, 4380),  # 이규찬 코너킥*키패스-박건 공중볼경합*슈팅
        (6720, 6900),  # 백승원 프리킥*슈팅
        (11130, 11820),  # 김영주 차단
        (14520, 14970),  # 강성우 돌파성공
        (15060, 16530),  # 강성우 골-박건 어시스트
        (20400, 20580),  # 박건 발리슛
        (20580, 21810),  # 이규찬 힐패스
        (23250, 24090),  # 손현승 키패스-강성우 유효슈팅
        (24420, 24900),  # 이준범 골-박건 어시스트
        (28290, 29070),  # 공격지역 연계
        (32640, 33330),  # 백승원 키패스-이규찬 슈팅
        (33990, 34350),  # 백승원 골
        (35340, 36450),  # 백승원 유효슈팅 후 주지홍 크로스 처리
        (37830, 38370),  # 박건 키패스-강성우 유효슈팅
        (45000, 45360),  # 백승원 스루패스
        (47430, 47940),  # 이규찬 스루패스-엄윤수 돌파
        (50820, 51270),  # 이준범 태클성공-박건 슈팅
    ]

    extract_and_cut_audio(input_media, cut_ranges, fps, output_audio_directory)

    # # 영상 자르기
    for idx, (start, end) in enumerate(cut_ranges, 1):
        output_cut = f'cut_video{idx}.mp4'
        cut_video(input_video, output_cut, start, end)

    # 경로 설정
    cut_video_files = [f"{output_video_directory}/cut_video_{idx + 1}.mp4" for idx in range(len(cut_ranges))]
    cut_audio_files = [f"{output_audio_directory}/cut_audio_{idx + 1}.mp3" for idx in range(len(cut_ranges))]
    merged_video_files = [f"{output_video_directory}/merged_video"]
    merge_audio_video(cut_video_files, cut_audio_files, output_merged_directory)

    merge_videos(output_merged_directory, merged_video_files)

    upscaled_video = f'{merged_video_files}-upscaled.mp4'
    final_output_video = f'{merged_video_files}-upscaled-with-audio.mp4'
    # 영상 해상도 업스케일
    upscale_video(merged_video_files, upscaled_video, scale_factor=2)
