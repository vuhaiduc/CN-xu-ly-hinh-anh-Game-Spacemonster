<h1 align="center">🎮 HỆ THỐNG GAME HÀNH ĐỘNG NHẬN DIỆN CỬ CHỈ TAY</h1>

<p align="center">
  <img src="assets/images/logoDaiNam.png" width="200"/>
  <img src="assets/images/LogoAIoTLab.png" width="170"/>
</p>

<div align="center">

[![Made by AIoTLab](https://img.shields.io/badge/Made%20by%20AIoTLab-blue?style=for-the-badge)]()
[![Fit DNU](https://img.shields.io/badge/Fit%20DNU-green?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-Game-yellow?style=for-the-badge)]()

</div>

---

## 1. 🌟 Giới thiệu

**Galactic Guardian** là một tựa game hành động 2D được phát triển bằng **Pygame**, kết hợp với **AI nhận diện cử chỉ tay** sử dụng **MediaPipe** và **OpenCV**.

Người chơi có thể:
- Điều khiển nhân vật bằng **cử chỉ tay qua webcam**
- Hoặc sử dụng **bàn phím (dự phòng)**

Game bao gồm:
- Hệ thống **5 màn chơi**
- **Boss nhiều giai đoạn (phase)**
- Cơ chế chiến đấu, né tránh, hồi máu
- Cốt truyện không gian hấp dẫn

---

## 2. 🚀 Chức năng chính

1. 🎥 **Nhận diện cử chỉ tay**
   - Sử dụng MediaPipe + OpenCV
   - Điều khiển nhân vật realtime

2. 🎮 **Gameplay hành động**
   - Di chuyển, tấn công, né tránh
   - Hệ thống máu và kỹ năng

3. 👾 **Hệ thống Enemy & Boss**
   - Enemy xuất hiện theo màn
   - Boss có **3 phase tăng độ khó**

4. 🌌 **Cốt truyện & hội thoại**
   - Mỗi boss có đoạn hội thoại riêng

5. 🧠 **Fallback điều khiển**
   - Có thể chơi bằng bàn phím nếu không dùng camera

---

## 3. 🎮 Cốt truyện

Năm 2157, Trái Đất nhận được tín hiệu cầu cứu từ rìa thiên hà.

Một thế lực bóng tối đang xâm chiếm vũ trụ.

Bạn là **Galactic Guardian** – chiến binh cuối cùng có khả năng cứu lấy thiên hà.

---

## 4. 🎯 Các màn chơi

| Màn | Tên | Boss |
|-----|-----|------|
| 1 | Vành Đai Sao Chổi | Comet Warden |
| 2 | Hành Tinh Lửa Ignis | Inferno Dragon |
| 3 | Tinh Vân Băng Giá Glacia | Frost Queen |
| 4 | Lõi Thiên Hà Điện Từ | Nebula Specter |
| 5 | Kỳ Quan Bóng Tối | Void Emperor |

---

## 5. ✋ Hệ thống cử chỉ

| Cử chỉ | Hành động |
|--------|-----------|
| ✊ Nắm đấm | Tấn công |
| ✋ Bàn tay mở | Né tránh |
| ☝️ Một ngón | Di chuyển phải |
| ✌️ Hai ngón | Di chuyển trái |
| 🤟 Ba ngón | Nhảy |
| 👍 Ngón cái | Hồi máu |
| 🔫 Súng | Bắn |

---

## 6. 🚀 Hướng dẫn cài đặt

```bash
# Clone project
git clone 

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy game
python main.py
```

**Lưu ý**: Đảm bảo máy tính có webcam để sử dụng tính năng điều khiển bằng cử chỉ tay.

---

## 7. ⚙️ Công nghệ sử dụng
🖥️ Phần mềm
Python
Pygame
OpenCV
MediaPipe
🧠 AI / Computer Vision
Hand Tracking (MediaPipe)
Gesture Recognition

## 8. Cấu trúc project

```
CNXSLA-SpaceShip10k/
project/
│── main.py
│── assets/
│── images/
│── sounds/
│── models/
│── utils/
│── requirements.txt
```
## 9. 🤝 Thành viên
| Họ và Tên | Vai trò |
|------------------------|--------------------------|
| Lê Bá Hoan | Phát triển mã nguồn, train model, kiểm thử, thực hiện video giới thiệu.|
| Vũ Hải Đức | Hỗ trợ Poster, Powerpoint, thuyết trình |

© 2026 NHÓM 8, CNTT 16-01, TRƯỜNG ĐẠI HỌC ĐẠI NAM
