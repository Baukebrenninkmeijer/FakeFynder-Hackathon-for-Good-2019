import cv2
import random
import glob

filepath = '/home/stijn/Desktop/uploads/000.mp4'

def select_frames(videopath, target_num_frames=50):
    # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    # fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    cap = cv2.VideoCapture(videopath)
    cap.set(1, 0)
    res, frame = cap.read()
    height, width, layers=frame.shape

    # video=cv2.VideoWriter('video.mp4',fourcc , 29.0, (height,width))#, False)
    video = cv2.VideoWriter('video.avi',fourcc, 29.0, (height,width))#, False)

    amount_of_frames = int(cap.get(7))
    print('amoutn of frames; ', amount_of_frames, target_num_frames)
    frame_list = random.sample(range(0, amount_of_frames-1), target_num_frames)
    print('frame_list: ', frame_list)

    for current_frame in frame_list:
        cap.set(1, current_frame)
        res, frame = cap.read()
        # video.write(frame)
        cv2.imwrite(str(current_frame)+'.jpg', frame)
    cap.release()

    for fname in glob.glob('*.jpg'):
        video.write(fname)
    video.release()

if __name__ == "__main__":
    select_frames(filepath)