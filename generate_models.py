import pandas as pd
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from scipy.sparse import hstack

CSV_FILE = 'enriched_churn_dataset.csv'
MODEL_DIR = 'model_artifacts'

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(CSV_FILE)
df['review_text'] = df['review_text'].fillna('')
df['avg_purchase_value'] = 1500
df['sentiment_score'] = 0.0

X_text = df['review_text']
X_num = df[['age','usage_frequency','num_purchases',
            'avg_purchase_value','sentiment_score',
            'satisfaction_score','num_support_tickets','tenure_days']]
y = df['churn']

vectorizer = TfidfVectorizer(max_features=100)
X_text_vec = vectorizer.fit_transform(X_text)

scaler = StandardScaler()
X_num_scaled = scaler.fit_transform(X_num)

X_final = hstack([X_text_vec, X_num_scaled])

model = LogisticRegression(solver='liblinear')
model.fit(X_final, y)

joblib.dump(model, f"{MODEL_DIR}/churn_model.pkl")
joblib.dump(vectorizer, f"{MODEL_DIR}/tfidf.pkl")
joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")

print("Models generated successfully")
