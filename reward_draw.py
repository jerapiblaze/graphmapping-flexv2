import pandas as pd
import matplotlib.pyplot as plt

# Config font
plt.rcParams["text.usetex"] = True
plt.rc('font', family='sans-serif')

labelsize, ticksize, legendsize = 30, 24, 23

# Đọc dữ liệu CSV
file_path = "/home/stu1/Code/graphmapping-flexv2/data/__internals__/QL/graphmapping_8cc97f88_nC135_ABI_10_a0.099_g0.01_n650envNew_rewards.csv"
df = pd.read_csv(file_path)

# Làm sạch tên cột
df.columns = df.columns.str.strip()

# Kiểm tra cột reward có tồn tại
if "reward" not in df.columns:
    raise ValueError("File CSV phải chứa cột 'reward'!")

# Rolling mean
window_size = 100
df["reward_mean"] = df["reward"].rolling(window=window_size, min_periods=1).mean()

# Vẽ figure
plt.figure(figsize=(10, 6))
plt.plot(df["ep"], df["reward_mean"],
         label=r"Average reward",
         color="forestgreen",
         linewidth=3)

# Trục & nhãn
# plt.ylim(0, None)
plt.xlabel("Episodes", fontsize=labelsize)
plt.ylabel("Average reward", fontsize=labelsize)
plt.tick_params(axis='x', labelsize=ticksize)
plt.tick_params(axis='y', labelsize=ticksize)

plt.grid()
plt.tight_layout()

plt.legend(fontsize=legendsize, loc="lower right")

plt.savefig("reward_single.pdf", dpi=300)
plt.show()
