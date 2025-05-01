
from PIL import Image
import cv2
import torch
from core.function import utils_rotate  # ✅ CŨNG ĐÚNG nếu đang chạy từ root project
from core.function import helper  # ✅ CŨNG ĐÚNG nếu đang chạy từ root project
import os
import torch
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
def detect_license_plate(image_path):
    # Load YOLOv5 models

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # thư mục gốc project
    model_path = os.path.join(BASE_DIR, 'core', 'model', 'LP_detector_nano_61.pt')
    yolo_LP_detect = torch.hub.load(
        'core/yolov5',
        'custom',
     path=model_path,
     force_reload=True,
        source='local'
    )
    ocr_model_path = os.path.join(BASE_DIR, 'core', 'model', 'LP_ocr_nano_62.pt')
    yolo_license_plate = torch.hub.load(
    'core/yolov5',
    'custom',
    path=ocr_model_path,
    force_reload=True,
    source='local'
    )

    yolo_license_plate.conf = 0.60

    # Read image
    frame = cv2.imread(image_path)
    plates = yolo_LP_detect(frame, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    list_read_plates = set()

    for plate in list_plates:
        x = int(plate[0])  # xmin
        y = int(plate[1])  # ymin
        w = int(plate[2] - plate[0])  # xmax - xmin
        h = int(plate[3] - plate[1])  # ymax - ymin
        crop_img = frame[y:y+h, x:x+w]
        cv2.imwrite("crop.jpg", crop_img)
        rc_image = cv2.imread("crop.jpg")

        lp = ""
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                if lp != "unknown":
                    list_read_plates.add(lp)
                    break
            if lp != "unknown":
                break

    return list_read_plates.pop() if list_read_plates else None