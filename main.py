import cv2
import numpy as np


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


if __name__ == "__main__":
    # 영상 자르기 예시
    input_video = 'IMG_1137.MOV'
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

    # 원하는 프레임 범위 지정
    cut_ranges = [
        (4050, 4650),
        (7020, 7890),
        (8160, 9000),
        (10950, 11820),
        (14010, 15120),
        (20820, 21210),
        (22260, 23370),
        (23760, 24570),
        (25620, 26040),
        (26820, 27540),
        (32370, 33240)

    ]

    # # 영상 자르기
    for idx, (start, end) in enumerate(cut_ranges, 1):
        output_cut = f'cut_video{idx}.mp4'
        cut_video(input_video, output_cut, start, end)

    # 자른 영상 목록
    video_list = ['IMG_1136.MOV',
                  'IMG_1136 2.MOV', 'IMG_1136 3.MOV', 'IMG_1136 4.MOV',
                  'IMG 1136 5.MOV']
    merged_video = 'merged_video1.mp4'

    # 영상 합치기
    merge_videos(video_list, merged_video)