import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler # 独热编码和标准化
from sklearn.neighbors import KNeighborsClassifier
import joblib

# 1. 加载数据集
heart_disease_data = pd.read_csv("./heart_disease.csv")

# 处理缺失值
heart_disease_data.dropna(inplace=True)

heart_disease_data.info()
print(heart_disease_data.head())

# 2. 数据集划分
# 划分特征和标签
X = heart_disease_data.drop("是否患有心脏病", axis=1)
y = heart_disease_data["是否患有心脏病"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

# 3. 特征工程
# 数值型特征
numerical_features = ["年龄", "静息血压", "胆固醇", "最大心率", "运动后的ST下降", "主血管数量"]
# 类别型特征
categorical_features = ["胸痛类型", "静息心电图结果", "峰值ST段的斜率", "地中海贫血"]
# 二元特征
binary_features = ["性别", "空腹血糖", "运动性心绞痛"]

# 创建一个列转换器
columnTransformer = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(drop="first"), categorical_features),
        ("bin", "passthrough", binary_features)
    ]
)

# 特征转换
X_train = columnTransformer.fit_transform(X_train)
X_test = columnTransformer.transform(X_test)

print(X_train.shape)
print(X_test.shape)

# # 4. 创建模型
# knn = KNeighborsClassifier(n_neighbors=3)
#
# # 5. 模型训练
# knn.fit(X_train, y_train)
#
# # 6. 模型评估，计算预测准确率
# score = knn.score(X_test, y_test)
# print(score)

# # 7. 保存模型
# joblib.dump(value=knn, filename="knn_model")

# # 加载模型，对新数据进行预测
# knn_loaded = joblib.load("knn_model")
# y_pred = knn_loaded.predict(X_test[10:11])
# print(f"预测类别：{y_pred}, 真实类别：{y_test[10]}")

# 创建KNN分类器
knn = KNeighborsClassifier()

# 定义网格搜索参数列表
param_grid = {"n_neighbors": list(range(1, 11)), "weights": ["uniform", "distance"]}

grid_search_cv = GridSearchCV(estimator=knn, param_grid=param_grid, cv=10)

# 模型训练
grid_search_cv.fit(X_train, y_train)

# 打印模型评估结果
results = pd.DataFrame(grid_search_cv.cv_results_).to_string()
print(results)
# 直接获取最佳模型和最佳得分
print(grid_search_cv.best_estimator_)
print(grid_search_cv.best_params_)
print(grid_search_cv.best_score_)

# 使用最佳模型，进行测试评估
knn = grid_search_cv.best_estimator_
print(knn.score(X_test, y_test))