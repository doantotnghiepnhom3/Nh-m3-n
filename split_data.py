import os
import shutil
import random

# 1. Cấu hình thư mục đầu vào từ MY_DATASET của bạn
source_img_dir = 'MY_DATASET/images'
source_label_dir = 'MY_DATASET/labels'
output_dir = 'YOLO_DATASET'  # Thư mục đích chuẩn YOLO

# 2. Tạo cấu trúc thư mục YOLO (Bao gồm cả tập test)
folders = [
    'train/images', 'train/labels',
    'val/images', 'val/labels',
    'test/images', 'test/labels'
]
for folder in folders:
    os.makedirs(os.path.join(output_dir, folder), exist_ok=True)

# 3. Lấy danh sách toàn bộ ảnh
all_images = [f for f in os.listdir(source_img_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

# Trộn ngẫu nhiên dữ liệu để đảm bảo tính khách quan
random.seed(42)
random.shuffle(all_images)

# 4. Tính toán số lượng theo tỉ lệ 70% / 20% / 10%
total_count = len(all_images)
train_end = int(total_count * 0.7)
val_end = train_end + int(total_count * 0.2)

train_images = all_images[:train_end]
val_images = all_images[train_end:val_end]
test_images = all_images[val_end:]

# Hàm copy file ảnh và file nhãn .txt tương ứng
def copy_files(image_list, split_name):
    for img_name in image_list:
        txt_name = os.path.splitext(img_name)[0] + '.txt'
        
        img_path = os.path.join(source_img_dir, img_name)
        txt_path = os.path.join(source_label_dir, txt_name)
        
        dest_img = os.path.join(output_dir, split_name, 'images', img_name)
        dest_txt = os.path.join(output_dir, split_name, 'labels', txt_name)
        
        # Copy ảnh
        shutil.copy(img_path, dest_img)
        
        # Copy file nhãn nếu tồn tại
        if os.path.exists(txt_path):
            shutil.copy(txt_path, dest_txt)
        else:
            print(f"⚠️ Cảnh báo: Không tìm thấy file nhãn cho '{img_name}'")

# 5. Tiến hành chia và copy dữ liệu
print(f"📊 Tổng số ảnh trong dataset gốc: {total_count}")
print(f"  --> Chia sang Train (70%): {len(train_images)} ảnh")
print(f"  --> Chia sang Val   (20%): {len(val_images)} ảnh")
print(f"  --> Chia sang Test  (10%): {len(test_images)} ảnh")

copy_files(train_images, 'train')
copy_files(val_images, 'val')
copy_files(test_images, 'test')

print(f"\n✅ Hoàn tất! Dữ liệu đã được chia chuẩn vào thư mục '{output_dir}'.")