import os
import cv2
import torch
import numpy as np
import cloudinary.uploader
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from core.function import utils_rotate, helper
from core.models import Vehicle
import warnings
import logging

warnings.filterwarnings("ignore", category=FutureWarning)
logger = logging.getLogger(__name__)

# Global model cache
yolo_LP_detect = None
yolo_license_plate = None

def load_models():
    global yolo_LP_detect, yolo_license_plate
    model_path = os.path.join(settings.BASE_DIR, 'core', 'model', 'LP_detector_nano_61.pt')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    yolo_LP_detect = torch.hub.load(
        'core/yolov5', 'custom', path=model_path, force_reload=True, source='local'
    )
    ocr_model_path = os.path.join(settings.BASE_DIR, 'core', 'model', 'LP_ocr_nano_62.pt')
    if not os.path.exists(ocr_model_path):
        raise FileNotFoundError(f"Model not found: {ocr_model_path}")
    yolo_license_plate = torch.hub.load(
        'core/yolov5', 'custom', path=ocr_model_path, force_reload=True, source='local'
    )
    yolo_license_plate.conf = getattr(settings, 'LICENSE_PLATE_CONFIDENCE', 0.60)

# Load models at startup
load_models()

def get_next_image_number():
    """
    Find the next available sequential number for image filenames in media/temp/.
    Returns: int (e.g., 1 for 1.jpg, 2 for 2.jpg).
    """
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    if not default_storage.exists('temp'):
        return 1
    files = default_storage.listdir('temp')[1]  # Get files in temp/
    numbers = []
    for file in files:
        if file.endswith('.jpg'):
            try:
                num = int(file.split('.')[0])
                numbers.append(num)
            except ValueError:
                continue
    return max(numbers, default=0) + 1

def detect_license_plate(image_path):
    """
    Detect and read a license plate from an image, saving the cropped plate to media/temp/,
    uploading to Cloudinary, and returning the Cloudinary URL.
    Args:
        image_path (str): Path to the input image.
    Returns:
        tuple: (license_plate (str or None), cloudinary_url (str or None))
    """
    # Read image
    frame = cv2.imread(image_path)
    if frame is None:
        logger.error(f"Failed to read image: {image_path}")
        return None, None

    # Detect plates
    plates = yolo_LP_detect(frame, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    list_read_plates = set()
    cloudinary_url = None

    for plate in list_plates:
        x = int(plate[0])
        y = int(plate[1])
        w = int(plate[2] - plate[0])
        h = int(plate[3] - plate[1])

        # Validate bounding box
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > frame.shape[1] or y+h > frame.shape[0]:
            logger.warning(f"Invalid bounding box: x={x}, y={y}, w={w}, h={h}")
            continue

        # Process plate
        crop_img = frame[y:y+h, x:x+w]
        lp = ""
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                if lp != "unknown":
                    list_read_plates.add(lp.upper())  # Normalize to uppercase
                    break
            if lp != "unknown":
                break

        if lp != "unknown":
            # Check if vehicle with this license plate already has an image
            try:
                vehicle = Vehicle.objects.get(license_plate=lp)
                if vehicle.image:
                    cloudinary_url = vehicle.image
                    logger.info(f"Reusing existing Cloudinary URL for {lp}: {cloudinary_url}")
                    break
            except Vehicle.DoesNotExist:
                pass

            # Save cropped image to temp
            try:
                next_number = get_next_image_number()
                crop_filename = f"temp/{next_number}.jpg"
                crop_image_path = default_storage.save(crop_filename, ContentFile(cv2.imencode('.jpg', crop_img)[1].tobytes()))
                full_crop_path = os.path.join(settings.MEDIA_ROOT, crop_image_path)
                logger.info(f"Saved temp image for {lp}: {crop_image_path}")

                # Upload to Cloudinary
                try:
                    upload_result = cloudinary.uploader.upload(
                        full_crop_path,
                        folder="license_plates",  # Optional: Organize in Cloudinary
                        resource_type="image",
                        public_id=f"plate_{lp}_{next_number}"  # Unique ID for the image
                    )
                    cloudinary_url = upload_result['secure_url']
                    logger.info(f"Uploaded to Cloudinary: {cloudinary_url}")

                    # Delete local temp file
                    try:
                        default_storage.delete(crop_image_path)
                        logger.info(f"Deleted local temp file: {crop_image_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete local temp file {crop_image_path}: {e}")

                except Exception as e:
                    logger.error(f"Error uploading to Cloudinary: {e}")
                    cloudinary_url = None

            except Exception as e:
                logger.error(f"Error saving temp image {crop_filename}: {e}")
                cloudinary_url = None
                crop_image_path = None

    license_plate = list_read_plates.pop() if list_read_plates else None
    return license_plate, cloudinary_url
def detect_license_plate_checkout(image_path):
    """
    Detect and read a license plate from an image for checkout purposes.
    Does not save or upload images.
    Args:
        image_path (str): Path to the input image.
    Returns:
        str or None: License plate number if detected, None otherwise.
    """
    # Read image
    frame = cv2.imread(image_path)
    if frame is None:
        logger.error(f"Failed to read image: {image_path}")
        return None

    # Detect plates
    plates = yolo_LP_detect(frame, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    list_read_plates = set()

    for plate in list_plates:
        x = int(plate[0])
        y = int(plate[1])
        w = int(plate[2] - plate[0])
        h = int(plate[3] - plate[1])

        # Validate bounding box
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > frame.shape[1] or y+h > frame.shape[0]:
            logger.warning(f"Invalid bounding box: x={x}, y={y}, w={w}, h={h}")
            continue

        # Process plate
        crop_img = frame[y:y+h, x:x+w]
        lp = ""
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                if lp != "unknown":
                    list_read_plates.add(lp.upper())  # Normalize to uppercase
                    break
            if lp != "unknown":
                break

    return list_read_plates.pop() if list_read_plates else None