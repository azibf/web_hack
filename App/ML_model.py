import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

data = pd.read_csv(r'data_ml.csv')

X = data[['par1', 'par2', 'par3']]
Y = data.result
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.15, random_state=73)
rfc = RandomForestClassifier(n_estimators=70)
rfc.fit(x_train, y_train)