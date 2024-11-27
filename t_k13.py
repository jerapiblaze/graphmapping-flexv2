import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Đọc dữ liệu từ file CSV
df = pd.read_csv("/home/minhkeke/Code/tanh-code-fix/graphmapping-flexv2/data/results/20241005_144413.csv")

# Tách cột 'setname' để lấy tên mạng và cấu hình (C1, C3, C13)
df['network'] = df['setname'].apply(lambda x: x.split('_')[1])
df['config'] = df['setname'].apply(lambda x: x.split('_')[0])  # Lấy C1, C3, C13

# Chuyển tên các phương pháp thành định dạng bạn mong muốn
df['method'] = df['solvername'].replace({
    "GREEDY": "GREEDY"
})

# Lọc dữ liệu chỉ cho ILP
df = df[df['method'] == 'GREEDY']

# Danh sách các mạng và cấu hình
networks = ["COS", "PIO", "ATL", "ABI", "POL"]
configs = ["C1", "C3", "C13"]
networks_x_axis = ["COS_20", "PIO_20", "ATL_10", "ABI_10", "POL_10"]

# Màu sắc cho từng cấu hình
colors = {"C1": "lightblue", "C3": "lightgreen", "C13": "lightcoral"}
edge_colors = {"C1": "blue", "C3": "green", "C13": "red"}

# Tạo hình vẽ
fig, ax = plt.subplots(figsize=(10, 6))
width = 0.2  # Độ rộng của mỗi thanh

# Tọa độ x cho mỗi mạng và cấu hình
x = np.arange(len(networks))

# Vẽ biểu đồ cho từng cấu hình
for i, config in enumerate(configs):
    config_data = df[df['config'] == config]
    
    # Dữ liệu objvalue
    obj_values = [config_data[config_data['network'] == network]['objvalue'].sum() for network in networks]
    print(obj_values)
    # Vẽ cột cho từng cấu hình
    ax.bar(x + i * (width+0.02), obj_values, width, label=f'GREEDY {config}', 
           color=colors[config], edgecolor=edge_colors[config], linewidth=1.8)

# Cài đặt nhãn và tiêu đề
ax.set_axisbelow(True)
ax.set_axisbelow(True)
plt.grid(color='lightgrey', linestyle='--', zorder=0)
ax.set_xlabel('Networks - Numbers of slices')
ax.set_ylabel('Objective Value')
ax.set_xticks(x + width *1.1)
ax.set_xticklabels([r"" + network + "" for network in networks_x_axis])  # Sử dụng textsc cho tên mạng
ax.legend()

# Lưu biểu đồ dưới dạng file ảnh
plt.tight_layout()
plt.savefig("ilp_objective_value_comparison.pdf", dpi=300)

plt.show()
