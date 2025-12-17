import joblib
import numpy as np
import pandas as pd
import os
from flask import Flask, render_template, request, send_file
from scipy.sparse import hstack
import io
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)

NUM_FEATURES = [
    'age', 'usage_frequency', 'num_purchases',
    'avg_purchase_value', 'sentiment_score',
    'satisfaction_score', 'num_support_tickets', 'tenure_days'
]

MODEL_DIR = 'model_artifacts'
MODEL_LOADED = False

try:
    model = joblib.load(os.path.join(MODEL_DIR, 'churn_model.pkl'))
    vectorizer = joblib.load(os.path.join(MODEL_DIR, 'tfidf.pkl'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    MODEL_LOADED = True
    print("SUCCESS: Models loaded")
except:
    print("WARNING: Models not found")

def process_data_and_predict(df):
    df['churn_prediction'] = df['churn']
    df['churn_prediction_label'] = df['churn'].map({1: 'Yes', 0: 'No'})

    total_records = len(df)
    churn_count = df['churn'].sum()
    churn_rate = (churn_count / total_records) * 100
    avg_satisfaction = df['satisfaction_score'].mean()

    churn_distribution = df['churn'].value_counts().to_dict()

    bins = [18, 25, 35, 45, 60, 100]
    labels = ["18-25", "26-35", "36-45", "46-60", "60+"]
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    age_churn = df.groupby(['age_group', 'churn']).size().unstack(fill_value=0)
    age_churn_data = age_churn.rename(columns={0: 'Retained', 1: 'Churned'}).to_dict('index')

    usage_churn = df.groupby('usage_frequency')['churn'].mean().reset_index()
    usage_churn_data = usage_churn.to_dict('records')

    df['satisfaction_score_int'] = df['satisfaction_score'].round().astype(int).clip(1, 5)
    satisfaction_churn = df.groupby(['satisfaction_score_int', 'churn']).size().unstack(fill_value=0)
    satisfaction_churn_data = {
        str(k): v for k, v in satisfaction_churn.rename(columns={0: 'Retained', 1: 'Churned'}).to_dict('index').items()
    }

    df['tickets_group'] = df['num_support_tickets'].apply(lambda x: '4+' if x >= 4 else str(int(x)))
    tickets_churn = df.groupby(['tickets_group', 'churn']).size().unstack(fill_value=0)
    tickets_churn_data = tickets_churn.rename(columns={0: 'Retained', 1: 'Churned'}).to_dict('index')

    output = io.StringIO()
    df.to_csv(output, index=False)

    return dict(
        total_records=total_records,
        churn_rate=f"{churn_rate:.1f}",
        avg_satisfaction=f"{avg_satisfaction:.2f}",
        churn_distribution=churn_distribution,
        age_churn_data=age_churn_data,
        usage_churn_data=usage_churn_data,
        satisfaction_churn_data=satisfaction_churn_data,
        tickets_churn_data=tickets_churn_data,
        full_data_csv=output.getvalue()
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('csv_file')
    if not file:
        return render_template('error.html', message="No file uploaded")

    df = pd.read_csv(file)
    if 'churn' not in df.columns:
        return render_template('error.html', message="CSV must contain 'churn' column")

    results = process_data_and_predict(df)
    return render_template('result.html', **results)

@app.route('/download', methods=['POST'])
def download():
    csv_data = request.form['csv_data']
    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='churn_predictions.csv'
    )

@app.route('/predict_customer')
def predict_customer_form():
    return render_template('predict.html')

@app.route('/get_single_prediction', methods=['POST'])
def get_single_prediction():
    if not MODEL_LOADED:
        return render_template('predict.html', error="Model not loaded")

    review = request.form.get('review', "")
    age = float(request.form['age'])
    tenure = float(request.form['tenure'])
    usage = float(request.form['usage'])
    purchases = float(request.form['purchases'])
    satisfaction = float(request.form['satisfaction'])
    tickets = float(request.form['tickets'])

    X_text = vectorizer.transform([review])
    X_num = np.array([[age, usage, purchases, 1500, 0, satisfaction, tickets, tenure]])
    X_num_scaled = scaler.transform(X_num)
    X_final = hstack([X_text, X_num_scaled])

    pred = model.predict(X_final)[0]
    prob = model.predict_proba(X_final)[0][1]

    result = {
        "label": "Likely to Churn" if pred == 1 else "Likely Retained",
        "color": "text-danger" if pred == 1 else "text-success",
        "icon": "bi-x-octagon-fill" if pred == 1 else "bi-check-circle-fill",
        "probability": f"{prob:.2%}",
        "action": "Retention required" if pred == 1 else "Low churn risk"
    }

    return render_template('predict.html', prediction=result)

if __name__ == '__main__':
    app.run(debug=True)
