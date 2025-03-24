import pandas as pd
import matplotlib.pyplot as plt  # Correct import for matplotlib

df = pd.read_csv('Dataset.csv')

# Check null values
null_values = df.isnull().sum()
cols = df.columns
print("Columns:", cols)
print("\nNull values per column:")
print(null_values)

# Create scatter plot (corrected)
plt.figure(figsize=(10, 6))  # Optional: set figure size
plt.scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], color='red')  # Using iloc for column access
plt.title("Scatter Plot of First Two Columns")
plt.xlabel(cols[0])  # Use column name as x-axis label
plt.ylabel(cols[1])  # Use column name as y-axis label
plt.show()