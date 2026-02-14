import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression

# 1. 加载数据集
dataset = pd.read_csv('./train.csv')

# 测试图像
# digit = dataset.iloc[10, 1:].values
# plt.imshow( digit.reshape(28, 28), cmap='gray' )
# plt.show()

# 2. 划分数据集
X = dataset.drop('label', axis=1)
y = dataset['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

# 3. 特征工程：归一化
scaler = MinMaxScaler()
x_train = scaler.fit_transform(X_train)
x_test = scaler.transform(X_test)

# 4. 定义模型和训练
model = LogisticRegression(max_iter=500)
model.fit(x_train, y_train)

# 5. 模型评估
score = model.score(x_test, y_test)
print(score)

# 6. 测试（预测某个新图像表示的数字）
digit = x_test[123, :].reshape(1, -1)
print( model.predict(digit) )
print(y_test.iloc[123])
print( model.predict_proba(digit) )

# 画出图像
plt.imshow(digit.reshape(28, 28), cmap="gray")
plt.show()