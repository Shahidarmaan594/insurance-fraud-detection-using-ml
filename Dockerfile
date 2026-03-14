# Insurance Fraud Detection - Backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python data_generator.py && python train_model.py

EXPOSE 5000

CMD ["python", "app.py"]
