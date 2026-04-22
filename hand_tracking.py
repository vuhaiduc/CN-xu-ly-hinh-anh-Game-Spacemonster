# hand_tracking.py
import cv2
import threading
import time
import numpy as np
import pygame

try:
    import mediapipe as mp
except Exception:
    mp = None

from gesture import classify_gesture, GestureWithMotion, get_gesture_icon, gesture_to_action, get_gesture_description
from config import COLORS
from settings import (
    MIN_DETECTION_CONFIDENCE, 
    MIN_TRACKING_CONFIDENCE,
    PROCESS_INTERVAL,
    GESTURE_COOLDOWN,
    GESTURE_STABLE_THRESHOLD
)


class HandTracker:
    def __init__(self, camera_index=0, show_preview=False):
        self.available = False
        self.cap = None
        self.hands = None
        self.show_preview = show_preview
        self.last_gesture = None
        self.gesture_stable_count = 0
        self.gesture_cooldown = 0
        self.running = True
        self.preview_thread = None
        self.current_gesture = None
        self.current_swipe = None
        self.current_lift = False
        self.current_action = None
        self.frame_lock = threading.Lock()
        self.last_process_time = 0
        self.process_interval = PROCESS_INTERVAL
        self.current_frame = None
        
        self.motion_detector = GestureWithMotion()
        
        self.last_lift_detection = 0
        self.lift_cooldown = 15
        self.frame_counter = 0
        
        self.gesture_stable_threshold = GESTURE_STABLE_THRESHOLD
        
        # Thêm biến lưu vị trí tay
        self._last_hand_x = None
        self._hand_detected = False

        if mp is None:
            print("⚠️ MediaPipe not available. Please install: pip install mediapipe")
            return

        print(f"📷 Đang mở camera index {camera_index}...")
        
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            print(f"❌ Không thể mở camera {camera_index}")
            self.cap = None
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        ret, test_frame = self.cap.read()
        if not ret or test_frame is None:
            print(f"❌ Camera không đọc được frame")
            self.cap.release()
            self.cap = None
            return
        
        print(f"✅ Camera OK - {test_frame.shape[1]}x{test_frame.shape[0]}")
        
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        self.available = True
        print("✅ HandTracker sẵn sàng")
        
        self.start_camera_thread()

    def start_camera_thread(self):
        self.running = True
        self.preview_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.preview_thread.start()
        print("📷 Camera thread started")

    def _camera_loop(self):
        while self.running and self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue
            
            frame = cv2.flip(frame, 1)
            self.frame_counter += 1
            
            current_time = time.time()
            if current_time - self.last_process_time >= self.process_interval:
                self.last_process_time = current_time
                
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb)
                
                gesture = None
                swipe = None
                is_lift = False
                action = None
                hand_x = None
                hand_detected = False
                
                if results.multi_hand_landmarks:
                    landmarks = results.multi_hand_landmarks[0]
                    hand_detected = True
                    
                    # Lấy vị trí X của cổ tay (landmark 0)
                    wrist_x = landmarks.landmark[0].x
                    hand_x = wrist_x
                    
                    gesture = classify_gesture(landmarks)
                    
                    if gesture == "fist":
                        swipe = self.motion_detector.detect_swipe(landmarks)
                    
                    # Xử lý đúng giá trị trả về từ detect_lift()
                    is_lift = False
                    if gesture == "one_index":
                        lift_result = self.motion_detector.detect_lift(landmarks)
                        is_lift = (lift_result == "lift")
                    
                    action = gesture_to_action(gesture, is_lift, swipe)
                    
                    self.mp_draw.draw_landmarks(
                        frame, landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                        self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
                    )
                    
                    if gesture == self.last_gesture:
                        self.gesture_stable_count += 1
                    else:
                        self.gesture_stable_count = 0
                        self.last_gesture = gesture
                    
                    if self.gesture_cooldown > 0:
                        self.gesture_cooldown -= 1
                        gesture = None
                        action = None
                    elif self.gesture_stable_count >= self.gesture_stable_threshold:
                        self.gesture_cooldown = GESTURE_COOLDOWN
                    
                    with self.frame_lock:
                        self.current_gesture = gesture
                        self.current_swipe = swipe
                        self.current_lift = is_lift
                        self.current_action = action
                        self._last_hand_x = hand_x
                        self._hand_detected = hand_detected
                else:
                    self.gesture_stable_count = max(0, self.gesture_stable_count - 1)
                    if self.gesture_stable_count == 0:
                        with self.frame_lock:
                            self.current_gesture = None
                            self.current_swipe = None
                            self.current_lift = False
                            self.current_action = None
                            self.last_gesture = None
                            self.motion_detector.prev_position = None
                            self.motion_detector.prev_y = None
                            self._hand_detected = False
            
            self._draw_info(frame)
            self.current_frame = frame
            
            time.sleep(0.005)
        
        if self.cap:
            self.cap.release()

    def read_gesture(self):
        if not self.available or self.cap is None:
            return None, None
        
        with self.frame_lock:
            gesture = self.current_gesture
            action = self.current_action
        
        return gesture, action
    
    def get_hand_position(self):
        """Lấy vị trí X của bàn tay (giá trị 0-1 theo chiều ngang)"""
        if not self.available:
            return None
        
        with self.frame_lock:
            if self._hand_detected:
                return self._last_hand_x
        return None
    
    def is_hand_detected(self):
        """Kiểm tra có đang phát hiện tay không"""
        if not self.available:
            return False
        with self.frame_lock:
            return self._hand_detected

    def _draw_info(self, frame):
        try:
            h, w = frame.shape[:2]
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 170), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            with self.frame_lock:
                gesture = self.current_gesture
                swipe = self.current_swipe
                is_lift = self.current_lift
                action = self.current_action
                hand_detected = self._hand_detected
            
            # Hiển thị trạng thái phát hiện tay
            if hand_detected:
                cv2.putText(frame, "✋ HAND DETECTED", (10, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)
            else:
                cv2.putText(frame, "❌ NO HAND", (10, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 1)
            
            cv2.putText(frame, "=== GESTURE CONTROLS ===", (10, 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            
            guides = [
                ("✊ NAM DAM", "ĐẤM"),
                ("✊ + VUOT", "DI CHUYEN"),
                ("☝️ 1 NGON + KEO LEN", "NHẢY"),
                ("✌️ 2 NGON", "BAN"),
                ("🤟 3 NGON", "HOI MAU"),
                ("👍 NGON CAI", "CHIEU CUOI"),
            ]
            
            for i, (action_text, desc) in enumerate(guides):
                is_active = False
                if gesture:
                    if "NAM DAM" in action_text and gesture == "fist" and not swipe:
                        is_active = True
                    elif "NAM DAM + VUOT" in action_text and gesture == "fist" and swipe:
                        is_active = True
                    elif "1 NGON" in action_text and gesture == "one_index" and is_lift:
                        is_active = True
                    elif "2 NGON" in action_text and gesture == "two_fingers":
                        is_active = True
                    elif "3 NGON" in action_text and gesture == "three_fingers":
                        is_active = True
                    elif "NGON CAI" in action_text and gesture == "thumbs_up":
                        is_active = True
                
                color = (0, 255, 0) if is_active else (150, 150, 150)
                cv2.putText(frame, f"{action_text}", (10, 85 + i * 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                cv2.putText(frame, f"{desc}", (250, 85 + i * 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
            
            if action:
                y_offset = 85 + len(guides) * 20 + 15
                
                if action == "jump":
                    cv2.putText(frame, f">>> ⬆️ NHẢY! <<<", (w - 200, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif action == "attack":
                    cv2.putText(frame, f">>> ✊ ĐẤM! <<<", (w - 180, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif action == "left":
                    cv2.putText(frame, f">>> ⬅️ SANG TRÁI <<<", (w - 220, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif action == "right":
                    cv2.putText(frame, f">>> ➡️ SANG PHẢI <<<", (w - 220, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif action == "shoot":
                    cv2.putText(frame, f">>> ✌️ BẮN! <<<", (w - 180, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif action == "heal":
                    cv2.putText(frame, f">>> 🤟 HỒI MÁU! <<<", (w - 200, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif action == "ultimate":
                    cv2.putText(frame, f">>> 👍 CHIÊU CUỐI! <<<", (w - 220, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
        except Exception as e:
            pass

    def get_frame_surface(self, size=(320, 240)):
        if self.current_frame is None:
            return None
        
        try:
            frame = cv2.resize(self.current_frame, size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            return frame_surface
        except Exception as e:
            return None

    def set_preview(self, enabled):
        self.show_preview = enabled

    def get_frame(self):
        return self.current_frame

    def release(self):
        print("🔄 Đang giải phóng camera...")
        self.running = False
        
        if self.preview_thread and self.preview_thread.is_alive():
            self.preview_thread.join(timeout=1)
        
        if self.cap is not None:
            self.cap.release()
        
        if self.hands is not None:
            self.hands.close()
        
        print("✅ Camera released")