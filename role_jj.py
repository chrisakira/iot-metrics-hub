import pandas as pd

import matplotlib.pyplot as plt

# Read the CSV file
data = pd.read_csv('./pressao.csv', sep=';', usecols=[0,1] ,header=0)  # Assuming the CSV file has a header

# If the column names are different, adjust them as needed
if 'col_1' not in data.columns or 'col_2' not in data.columns:
    data.columns = ['col_1', 'col_2']  # Adjust the column names as needed

data_1 = data['col_1']
data_2 = data['col_2']

data_index = len(data_1)
initial_index = int(data_1.idxmax() + data_1.idxmax()*0.1)

min = int(0)
max = int(0)

i = initial_index
while i < data_index-1:
    if data_2[i+1] < (data_2[i]+5):
        max = data_1[i]    
        break
    i += 1
    
i = initial_index
while i < data_index:
    if (data_1[i] < data_2[i]):
        min = data_1[i]
        break
    i += 1
    
print(max)    
print(min)

# Plot the data
# Add circles at specific points
plt.plot(data_1.index, data_1, color='black')
plt.plot(data_2.index, data_2, color='blue')
plt.axhline(y=max, color='r', linestyle='--')
plt.axhline(y=min, color='g', linestyle='--')
plt.text(len(data_1)*0.9, max, 'Max Pressure', color='r', ha='left', va='bottom')
plt.text(len(data_1)*0.9, min, 'Min Pressure', color='g', ha='left', va='bottom')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Data Plot')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

# Save the plot as a PNG file
plt.savefig('./plot.png')
