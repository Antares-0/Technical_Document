import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler    # 标准化
from sklearn.linear_model import LinearRegression, SGDRegressor # 线性回归模型：正规方程法和SGD
from sklearn.metrics import mean_squared_error  # 均方误差损失函数

# 1. 读取数据集
dataset = pd.read_csv("./advertising.csv")

dataset.dropna(inplace=True)
dataset.drop(columns=dataset.columns[0], axis=1, inplace=True)

dataset.info()
print(dataset.head())

# 2. 划分数据集
X = dataset.drop(columns='Sales', axis=1)
y = dataset['Sales']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

# 3. 特征工程：标准化
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 4. 创建模型并训练
# 4.1 正规方程法
model_lr = LinearRegression()
model_lr.fit(X_train, y_train)

print("LR Coefficients: ", model_lr.coef_)
print("LR Intercept: ", model_lr.intercept_)

# 4.2 SGD
model_sgd = SGDRegressor()
model_sgd.fit(X_train, y_train)

print("SGD Coefficients: ", model_sgd.coef_)
print("SGD Intercept: ", model_sgd.intercept_)

# 5. 预测
y_pred1 = model_lr.predict(X_test)
y_pred2 = model_sgd.predict(X_test)

# 6. 使用均方误差评价模型
print("LR Mean Squared Error: ", mean_squared_error(y_test, y_pred1))
print("SGD Mean Squared Error: ", mean_squared_error(y_test, y_pred2))

print(model_lr.score(X_test, y_test))
print(model_sgd.score(X_test, y_test))