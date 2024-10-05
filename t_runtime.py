import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Đọc dữ liệu từ file CSV
df = pd.read_csv("/home/minhkeke/Code/tanh-code-fix/graphmapping-flexv2/data/results/20241004_105458.csv")

# Tách cột 'setname' để lấy tên mạng
df['network'] = df['setname'].apply(lambda x: x.split('_')[1])

# Chuyển tên các phương pháp thành định dạng bạn mong muốn
df['method'] = df['solvername'].replace({
    "QL_ILP": "QL-ILP", 
    "QL_CLC": "QL-CLC",
    "GREEDY": "CLC",
    "ILP_GUROBI"   : "ILP",
})

# Danh sách các mạng và phương pháp
networks = [ "COS","PIO",  "ATL", "ABI", "POL"]
networks_x_axis = [ "COS_20","PIO_20",  "ATL_10", "ABI_10", "POL_10"]
methods = ["ILP", "QL-ILP", "CLC", "QL-CLC"]

# Màu sắc và hatch cho từng phương pháp
colors_edge = {"ILP": "darkgray", "QL-ILP": "darkgreen", "CLC": "#1f77b4", "QL-CLC": "darkorange"}

hatches = {"ILP": ".", "QL-ILP": "", "CLC": "\\" , "QL-CLC": "/"}

# Tạo hình vẽ
fig, ax = plt.subplots(figsize=(8, 6))
width = 0.2  # Độ rộng của mỗi thanh

# Tọa độ x cho mỗi mạng và phương pháp
x = np.arange(len(networks))

# Vẽ biểu đồ cho từng phương pháp
for i, method in enumerate(methods):
    method_data = df[df['method'] == method]
    runtime_value = [method_data[method_data['network'] == network]['runtime'].sum() for network in networks]

    
    ax.bar(x + i * (width+0.02), runtime_value, width, label=f'{method}', color="w", edgecolor=colors_edge[method], hatch=hatches[method], linewidth=1.8)

# Cài đặt nhãn và tiêu đề

ax.set_axisbelow(True)
plt.grid(color='lightgrey', linestyle='--', zorder=0)
ax.set_xlabel('Networks - Number of slices')
ax.set_ylabel('Runtime (s)')
ax.set_yscale("log")
ax.set_xticks(x + width * 1.6)
ax.set_xticklabels([r"" + network + "" for network in networks_x_axis])  
ax.legend()

# Lưu biểu đồ dưới dạng file ảnh
plt.tight_layout()
plt.savefig("Runtime.png", dpi=300)  


plt.show()
