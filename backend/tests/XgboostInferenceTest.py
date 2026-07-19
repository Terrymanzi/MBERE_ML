import xgboost as xgb
import numpy as np
import joblib, tempfile, os

print("xgboost version:", xgb.__version__)
print("xgboost file:", xgb.__file__)

# Train + save + reload a throwaway model, entirely local -- no Colab, no git, no OneDrive involved.
X = np.random.rand(50, 4)
y = np.random.randint(0, 3, 50)
clf = xgb.XGBClassifier(n_estimators=5, max_depth=2, objective="multi:softprob", num_class=3)
clf.fit(X, y)

tmp_path = os.path.join(tempfile.gettempdir(), "xgb_roundtrip_test.pkl")
joblib.dump(clf, tmp_path)
reloaded = joblib.load(tmp_path)
print("round-trip OK:", reloaded.predict(X[:5]))