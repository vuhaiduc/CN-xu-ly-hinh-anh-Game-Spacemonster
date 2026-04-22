# gesture.py
import math
from settings import SWIPE_THRESHOLD, LIFT_THRESHOLD, MOTION_COOLDOWN

def _finger_up(hand_landmarks, tip, pip):
    return hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y

def _finger_down(hand_landmarks, tip, pip):
    return hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip].y

def _thumb_up_right(hand_landmarks, thumb_tip, thumb_ip):
    return hand_landmarks.landmark[thumb_tip].x > hand_landmarks.landmark[thumb_ip].x

def _thumb_up_left(hand_landmarks, thumb_tip, thumb_ip):
    return hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_ip].x

def get_hand_center(hand_landmarks):
    """Lấy tọa độ tâm bàn tay"""
    wrist = hand_landmarks.landmark[0]
    middle_mcp = hand_landmarks.landmark[12]
    return ((wrist.x + middle_mcp.x) / 2, (wrist.y + middle_mcp.y) / 2)


class GestureWithMotion:
    def __init__(self):
        self.prev_position = None
        self.prev_y = None
        self.prev_x = None
        self.swipe_threshold = SWIPE_THRESHOLD
        self.lift_threshold = LIFT_THRESHOLD
        self.frame_count = 0
        self.cooldown = MOTION_COOLDOWN
        
    def detect_swipe(self, hand_landmarks):
        """Phát hiện vuốt tay trái/phải/lên/xuống"""
        if hand_landmarks is None:
            self.prev_position = None
            self.prev_x = None
            self.prev_y = None
            return None
            
        current_pos = get_hand_center(hand_landmarks)
        
        if self.prev_position is None:
            self.prev_position = current_pos
            self.prev_x = current_pos[0]
            self.prev_y = current_pos[1]
            return None
        
        dx = current_pos[0] - self.prev_position[0]
        dy = current_pos[1] - self.prev_position[1]
        self.prev_position = current_pos
        
        self.frame_count += 1
        if self.frame_count < self.cooldown:
            return None
            
        # Ưu tiên phát hiện vuốt ngang trước
        if abs(dx) > self.swipe_threshold and abs(dx) > abs(dy):
            self.frame_count = 0
            if dx > 0:
                return "swipe_right"
            else:
                return "swipe_left"
        # Phát hiện vuốt dọc
        elif abs(dy) > self.swipe_threshold:
            self.frame_count = 0
            if dy > 0:
                return "swipe_down"
            else:
                return "swipe_up"
        
        return None
    
    def detect_lift(self, hand_landmarks):
        """Phát hiện kéo ngón tay lên (jump) - trả về 'lift' hoặc None"""
        if hand_landmarks is None:
            self.prev_y = None
            return None
            
        index_tip = hand_landmarks.landmark[8]
        current_y = index_tip.y
        
        if self.prev_y is None:
            self.prev_y = current_y
            return None
        
        dy = self.prev_y - current_y
        self.prev_y = current_y
        
        if dy > self.lift_threshold:
            self.frame_count = 0
            return "lift"
        
        return None


def classify_gesture(hand_landmarks):
    """
    Phân loại cử chỉ tĩnh
    """
    if hand_landmarks is None:
        return None

    TIPS = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
    PIPS = {"thumb": 2, "index": 6, "middle": 10, "ring": 14, "pinky": 18}

    index_up = _finger_up(hand_landmarks, TIPS["index"], PIPS["index"])
    middle_up = _finger_up(hand_landmarks, TIPS["middle"], PIPS["middle"])
    ring_up = _finger_up(hand_landmarks, TIPS["ring"], PIPS["ring"])
    pinky_up = _finger_up(hand_landmarks, TIPS["pinky"], PIPS["pinky"])
    
    thumb_up = _thumb_up_right(hand_landmarks, TIPS["thumb"], PIPS["thumb"])
    
    fist = not index_up and not middle_up and not ring_up and not pinky_up
    fingers_up = sum([index_up, middle_up, ring_up, pinky_up])
    
    if fist:
        return "fist"
    elif thumb_up and not index_up and not middle_up:
        return "thumbs_up"
    elif fingers_up == 1 and index_up and not middle_up:
        return "one_index"
    elif fingers_up == 2 and index_up and middle_up:
        return "two_fingers"
    elif fingers_up >= 3:
        return "three_fingers"
    
    return None


def gesture_to_action(gesture, is_lift=False, swipe=None):
    """Chuyển đổi cử chỉ thành hành động - Hỗ trợ cả menu và gameplay"""
    
    # ===== MENU ACTIONS =====
    if swipe == "swipe_up":
        return "menu_up"
    if swipe == "swipe_down":
        return "menu_down"
    
    # ===== GAMEPLAY ACTIONS =====
    # Nắm tay không vuốt = đấm cận chiến
    if gesture == "fist" and not swipe:
        return "attack"
    
    # Nắm tay + vuốt = di chuyển nhanh
    if gesture == "fist" and swipe:
        if swipe == "swipe_left":
            return "left"
        elif swipe == "swipe_right":
            return "right"
    
    # Một ngón + kéo lên = nhảy
    if gesture == "one_index" and is_lift:
        return "jump"
    
    # Xác nhận / chọn (cho menu và gameplay)
    if gesture in ["fist", "thumbs_up"] and not swipe:
        return "select"
    
    # Quay lại
    if gesture == "three_fingers":
        return "back"
    
    # Các cử chỉ khác
    actions = {
        "two_fingers": "shoot",
        "thumbs_up": "ultimate",
    }
    return actions.get(gesture)


def get_gesture_icon(gesture):
    icons = {
        "fist": "✊",
        "one_index": "☝️",
        "two_fingers": "✌️",
        "three_fingers": "🤟",
        "thumbs_up": "👍",
        "swipe_left": "⬅️",
        "swipe_right": "➡️",
        "swipe_up": "⬆️",
        "swipe_down": "⬇️",
        "lift": "⬆️",
    }
    return icons.get(gesture, "❓")


def get_gesture_description(gesture):
    descriptions = {
        "fist": "NẮM ĐẤM - ĐẤM",
        "fist_swipe": "NẮM ĐẤM + VUỐT - DI CHUYỂN",
        "one_index": "1 NGÓN + KÉO LÊN - NHẢY",
        "two_fingers": "2 NGÓN - BẮN",
        "three_fingers": "3 NGÓN - QUAY LẠI",
        "thumbs_up": "NGÓN CÁI - CHIÊU CUỐI",
        "swipe_left": "SANG TRÁI",
        "swipe_right": "SANG PHẢI",
        "swipe_up": "LÊN TRÊN",
        "swipe_down": "XUỐNG DƯỚI",
        "lift": "NHẢY",
    }
    return descriptions.get(gesture, gesture)