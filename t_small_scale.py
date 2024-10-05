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
networks = ["ATL", "ABI", "POL"]
networks_x_axis = ["ATL_10", "ABI_10", "POL_10"]
methods = ["ILP", "QL-ILP", "CLC", "QL-CLC"]

# Màu sắc và hatch cho từng phương pháp
colors_edge = {"ILP": "peru","QL-ILP": "darkgreen", "QL-CLC": "darkorange", "CLC": "#1f77b4"}
colors={"ILP": "lightyellow","QL-ILP": "aquamarine", "QL-CLC": "bisque", "CLC": "#aec7e8"}

hatches = {"ILP": ".", "QL-ILP": "", "CLC": "\\" , "QL-CLC": "/"}

# Tạo hình vẽ
fig, ax = plt.subplots(figsize=(8, 6))
width = 0.2  # Độ rộng của mỗi thanh

# Tọa độ x cho mỗi mạng và phương pháp
x = np.arange(len(networks))

# Vẽ biểu đồ cho từng phương pháp
for i, method in enumerate(methods):
    method_data = df[df['method'] == method]
    
    # Dữ liệu k1 và k3
    k1_values = [method_data[method_data['network'] == network]['k1'].sum() / 10 for network in networks]
    k3_values = [method_data[method_data['network'] == network]['k3'].sum() / 10 for network in networks]
    
    # Vẽ cột cho k1 và k3 với cùng màu và hatch
    ax.bar(x + i * (width+0.02), k1_values, width, label=f'{method} (k1)', color="w", edgecolor=colors_edge[method], hatch=hatches[method], linewidth=1.8, bottom=k3_values)
    ax.bar(x + i * (width+0.02), k3_values, width, label=f'{method} (k3)', color=colors[method], edgecolor=colors_edge[method], hatch=hatches[method], linewidth=1.8)

# Cài đặt nhãn và tiêu đề

ax.set_axisbelow(True)
ax.set_ylim(top=1)
plt.grid(color='lightgrey', linestyle='--', zorder=0)
ax.set_xlabel('Small-scale Network')
ax.set_ylabel('Acceptance Rate')
ax.set_xticks(x + width * 1.6)
ax.set_xticklabels([r"" + network + "" for network in networks_x_axis])  # Sử dụng textsc cho tên mạng
ax.legend()

# Lưu biểu đồ dưới dạng file ảnh
plt.tight_layout()
plt.savefig("acceptance_rate_comparison.pdf", dpi=300)  # Thay /path/to/save/ bằng đường dẫn bạn muốn lưu file


plt.show()
