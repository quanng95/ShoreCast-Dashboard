import pandas as pd

# Đọc file CSV
df = pd.read_csv(r"C:\Project\CoastSat-master\dashboard\data\Method3\CATALANGA\Column1Graph\time_series_data.csv")

# Sửa dates dựa trên year
df['dates'] = pd.to_datetime(df['year'].astype(str) + '-01-01')

# Lưu lại file
df.to_csv(r"C:\Project\CoastSat-master\dashboard\data\Method3\CATALANGA\Column1Graph\time_series_data.csv", index=False)

print("✅ Fixed CSV successfully!")