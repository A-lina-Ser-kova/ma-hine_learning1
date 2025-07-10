FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         build-essential \
         ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Linear_Regression.pkl/ ./
COPY main.py .

EXPOSE 8001

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8001"]
