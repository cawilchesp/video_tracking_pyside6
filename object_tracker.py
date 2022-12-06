import argparse
import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn

from utils.datasets import LoadStreams, LoadImages
from utils.general import non_max_suppression, scale_coords
from utils.torch_utils import select_device, time_synchronized

from models.models import *
from utils.datasets import *
from utils.general import *

from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.deep_sort import DeepSort
from collections import deque

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

data_deque = {}

def xyxy_to_xywh(*xyxy):
    """" Calculates the relative bounding box from absolute pixel values. """
    bbox_left = min([xyxy[0].item(), xyxy[2].item()])
    bbox_top = min([xyxy[1].item(), xyxy[3].item()])
    bbox_w = abs(xyxy[0].item() - xyxy[2].item())
    bbox_h = abs(xyxy[1].item() - xyxy[3].item())
    x_c = (bbox_left + bbox_w / 2)
    y_c = (bbox_top + bbox_h / 2)
    w = bbox_w
    h = bbox_h

    return x_c, y_c, w, h


def xyxy_to_tlwh(bbox_xyxy):
    tlwh_bboxs = []
    for i, box in enumerate(bbox_xyxy):
        x1, y1, x2, y2 = [int(i) for i in box]
        top = x1
        left = y1
        w = int(x2 - x1)
        h = int(y2 - y1)
        tlwh_obj = [top, left, w, h]
        tlwh_bboxs.append(tlwh_obj)

    return tlwh_bboxs


def compute_color(label: str) -> tuple:
    """
    Simple function that adds fixed color depending on the class
    """
    if label == 0: #person  #BGR
        color = (85, 45, 255)
    elif label == 1: #bicycle
        color = (7, 127, 15)
    elif label == 2: # Car
        color = (255, 149, 0)
    elif label == 3:  # Motobike
        color = (0, 204, 255)
    elif label == 5:  # Bus
        color = (0, 149, 255)
    elif label == 7:  # truck
        color = (222, 82, 175)
    # else:
    #     color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
    return color


def draw_trajectories(img: np.array, bbox: np.array, object_id: np.array,
                identities: np.array, trailslen: int) -> None:
    # Remove tracked point from buffer if object is lost
    for key in list(data_deque):
        if key not in identities:
            data_deque.pop(key)

    for i, box in enumerate(bbox):
        x1, y1, x2, y2 = [int(i) for i in box]
        center = (int((x2+x1)/2), int((y2+y1)/2))
        id = int(identities[i]) if identities is not None else 0
        if id not in data_deque:
            data_deque[id] = deque(maxlen=trailslen)
        color = compute_color(object_id[i])
        data_deque[id].appendleft(center)
 
        # Draw trajectory
        for i in range(1, len(data_deque[id])):
            if data_deque[id][i-1] is None or data_deque[id][i] is None:
                continue

            # thickness = int(np.sqrt(opt.trailslen/float(i+i))*1.5)
            cv2.line(img, data_deque[id][i-1], data_deque[id][i], color, 2)


def draw_boxes(img: np.array, bbox: np.array, object_id: np.array,
                identities: np.array) -> None:
    for i, box in enumerate(bbox):
        x1, y1, x2, y2 = [int(i) for i in box]
        id = int(identities[i]) if identities is not None else 0
        color = compute_color(object_id[i])
        label = f'{names[object_id[i]]} {id}'

        # Draw box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

        # Draw labels
        t_size = cv2.getTextSize(label, 0, 2/3, 1)[0]
        cv2.rectangle(img, (x1, y1-t_size[1]-3), (x1 + t_size[0], y1+3), color, -1, cv2.LINE_AA)
        cv2.putText(img, label, (x1, y1 - 2), 0, 2/3, [225, 255, 255], 1, cv2.LINE_AA)


def save_objects(bbox: np.array, object_id: np.array, identities: np.array, 
                    txt_path: str, frame_num: int) -> None:
    for i, box in enumerate(bbox):
        x1, y1, x2, y2 = [int(i) for i in box]

        id = int(identities[i]) if identities is not None else 0
        with open(txt_path + '.txt', 'a') as f:
            f.write(f'{frame_num},{id},{str(names[object_id[i]])},{x1},{y1},{x2-x1},{y2-y1},0,\n')


def load_classes(path):
    # Loads *.names file at 'path'
    with open(path, 'r') as f:
        names = f.read().split('\n')
    return list(filter(None, names))  # filter removes empty strings (such as last line)


def main(source, out, imgsz, device, view_img, trailslen):
    global names
    names = load_classes('data/coco.names')
    save_img = False

    # sources
    webcam = source == '0' or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

    # initialize deepsort
    cfg_deep = get_config()
    cfg_deep.merge_from_file("deep_sort_pytorch/configs/deep_sort.yaml")
    deepsort = DeepSort(cfg_deep.DEEPSORT.REID_CKPT,
                        max_dist=cfg_deep.DEEPSORT.MAX_DIST, min_confidence=cfg_deep.DEEPSORT.MIN_CONFIDENCE,
                        nms_max_overlap=cfg_deep.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg_deep.DEEPSORT.MAX_IOU_DISTANCE,
                        max_age=cfg_deep.DEEPSORT.MAX_AGE, n_init=cfg_deep.DEEPSORT.N_INIT, nn_budget=cfg_deep.DEEPSORT.NN_BUDGET,
                        use_cuda=True)

    # Initialize
    device = select_device(device) 
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    cfg = 'cfg/yolor_p6.cfg'
    weights = 'cfg/yolor_p6.pt'
    model = Darknet(cfg, imgsz).cuda()
    model.load_state_dict(torch.load(weights, map_location=device)['model'])
    model.to(device).eval()
    if half:
        model.half()  # to FP16

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = True
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
        print(f'Webcam: {dataset.w} X {dataset.h}, at {dataset.fps} FPS')
    else:
        save_img = True
        dataset = LoadImages(source, img_size=imgsz, auto_size=64)
    
    # Run inference
    frame_num = 0
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
    prevTime = 0
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img)[0]

        # Apply NMS
        conf_thres = 0.5
        iou_thres = 0.5
        classes = [0,1,2,3,5,7] # Filtro de clases: yolor_deepsort/data/coco.names
        pred = non_max_suppression(pred, conf_thres, iou_thres, False, classes, False)
        t2 = time_synchronized()

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
            else:
                p, s, im0 = path, '', im0s

            save_path = str(Path(out) / Path(p).name)
            txt_path = str(Path(out) / Path(p).stem)

            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                xywh_bboxs = []
                confs = []
                oids = []
                # Write results
                for *xyxy, conf, cls in det:
                    # to deep sort format
                    x_c, y_c, bbox_w, bbox_h = xyxy_to_xywh(*xyxy)
                    xywh_obj = [x_c, y_c, bbox_w, bbox_h]
                    xywh_bboxs.append(xywh_obj)
                    confs.append([conf.item()])
                    oids.append(int(cls))

                xywhs = torch.Tensor(xywh_bboxs)
                confss = torch.Tensor(confs)
                
                outputs = deepsort.update(xywhs, confss, oids, im0)
                if len(outputs) > 0:
                    bbox_xyxy = outputs[:, :4]
                    identities = outputs[:, -2]
                    object_id = outputs[:, -1]

                    draw_boxes(im0, bbox_xyxy, object_id, identities)
                    draw_trajectories(im0, bbox_xyxy, object_id, identities, trailslen)
                    save_objects(bbox_xyxy, object_id, identities, txt_path, frame_num)
                    
            # Print time (inference + NMS)
            print(f' Done. ({(t2 - t1):.3f} s)')

            currTime = time.time()
            fps = 1 / (currTime - prevTime)
            prevTime = currTime
            
            # Stream results
            if view_img:
                cv2.imshow(p, im0)

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'images':
                    cv2.imwrite(save_path, im0)
                else:
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer

                        fourcc = 'mp4v'  # output video codec
                        fps = vid_cap.get(cv2.CAP_PROP_FPS)
                        w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                    vid_writer.write(im0)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Esc to quit
            break
        frame_num += 1

    print('Done. (%.3fs)' % (time.time() - t0))


def detect(source, out, imgsz, device, view_img, trailslen):
    with torch.no_grad():
        main(source, out, imgsz, device, view_img, trailslen)
