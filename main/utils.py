from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np


class TrainModel:
    def __init__(self):
        self.model = LogisticRegression()

    def score_model(self, y_test, y_pred):
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred)

        print("Model Accuracy:", accuracy)
        print("Confusion Matrix:\n", conf_matrix)
        print("Classification Report:\n", class_report)
        return [accuracy, conf_matrix, class_report]

    def preprocess_column(self, col):
        def convert_value(value):
            try:
                # Convert fractions like '500/1000' to float
                if isinstance(value, str) and '/' in value:
                    num, denom = map(float, value.split('/'))
                    return num / denom
                # Convert percentages like '85%' to float
                if isinstance(value, str) and '%' in value:
                    return float(value.strip('%')) / 100
                # Convert currencies like '$1000' to float
                if isinstance(value, str) and value.startswith('$'):
                    return float(value.replace('$', '').replace(',', ''))
                # Return as float if possible
                return float(value)
            except (ValueError, TypeError):
                return value  # Return as-is if not convertible

        return col.apply(lambda x: convert_value(x))

    def preprocessing(self, data):
        label_encoders = {}
        for col in data.columns:
            if data[col].dtype == 'object':  # If column contains strings
                data[col] = self.preprocess_column(data[col])
                if data[col].dtype == 'object':  # Still non-numeric, apply LabelEncoder
                    le = LabelEncoder()
                    data[col] = le.fit_transform(data[col].astype(str))  # Convert all to string before encoding
                    label_encoders[col] = le
        data = data.replace('?', np.nan)
        return data, label_encoders

    def train_model(self, file, cols_to_drop):
        data = pd.read_csv(file)
        data.drop(columns=cols_to_drop, inplace=True)
        data, label_encoders = self.preprocessing(data)
        x = data.drop(columns=['fraud_reported'])
        x = x.apply(pd.to_numeric, errors='coerce')
        x.fillna(0, inplace=True)
        y = data['fraud_reported']
        scaler = StandardScaler()
        x = scaler.fit_transform(x)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        self.model.fit(x_train, y_train)
        y_pred = self.model.predict(x_test)
        result = self.score_model(y_test, y_pred)
        return self.model, data.drop(columns=['fraud_reported']).columns, label_encoders, scaler, result


class Predict:
    def __init__(self, inputs, model, label_encoders, scaler):
        self.model = model
        self.label_encoders = label_encoders
        self.scaler = scaler
        self.inputs = inputs

    def predict(self, cols):
        data = pd.DataFrame([self.inputs], columns=cols)
        for col in self.label_encoders:
            if col in data.columns:
                data[col] = self.label_encoders[col].transform(data[col].astype(str))

        # Scale the new data
        new_data = self.scaler.transform(data)
        prediction = self.model.predict(new_data)
        return prediction[0] == 1


