import random
import os

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Đọc nội dung của các tệp và lưu trữ trong các biến toàn cục
with open(os.path.join(current_dir, 'agents', 'desktop_agents.txt'), 'r') as desktop_file:
    desktop_agents = [line.strip() for line in desktop_file if line.strip()]

with open(os.path.join(current_dir, 'agents', 'mobile_agents.txt'), 'r') as mobile_file:
    mobile_agents = [line.strip() for line in mobile_file if line.strip()]

# Kết hợp cả hai danh sách User-Agent
all_agents = desktop_agents + mobile_agents

def get_random_user_agent(device_type='all'):
    """
    Trả về một User-Agent ngẫu nhiên dựa trên loại thiết bị.

    Tham số:
    - device_type (str): 'mobile' để lấy User-Agent di động, 'desktop' để lấy User-Agent máy tính để bàn,
                         'all' để lấy từ cả hai. Mặc định là 'all'.

    Trả về:
    - str: User-Agent ngẫu nhiên.
    """
    if device_type == 'mobile':
        return random.choice(mobile_agents)
    elif device_type == 'desktop':
        return random.choice(desktop_agents)
    else:
        return random.choice(all_agents)

# Ví dụ sử dụng
if __name__ == "__main__":
    print(get_random_user_agent('mobile'))  # Lấy User-Agent di động ngẫu nhiên
    print(get_random_user_agent('desktop')) # Lấy User-Agent máy tính để bàn ngẫu nhiên
    print(get_random_user_agent())          # Lấy User-Agent ngẫu nhiên từ cả hai loại
