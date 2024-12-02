from utils import read_video, save_video
from trackers import Tracker


def main():
    # Read Video
    video_frames = read_video('IMG_1172.MP4')

    # Initialize Tracker
    tracker = Tracker('models/best.pt')

    tracks = tracker.get_object_tracks(video_frames,
                                       read_from_stub=True,
                                       stub_path='stubs/track_stubs.pkl')

    # Draw output
    # Draw object Tracks
    output_video_frames = tracker.draw_annotations(video_frames, tracks)

    save_video(output_video_frames, output_video_path='output_videos/IMG_1172.avi')


if __name__ == "__main__":
    main()
