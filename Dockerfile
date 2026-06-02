# Gunakan base image Python 3.10 slim untuk menjaga ukuran container tetap kecil
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Install system dependencies yang dibutuhkan untuk membuild library python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt terlebih dahulu agar Docker dapat memanfaatkan cache layer
COPY requirements.txt .

# Install dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model agar loading chatbot saat pertama kali dijalankan lebih cepat
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy seluruh source code proyek ke dalam container
COPY . .

# Expose port default yang digunakan oleh Streamlit
EXPOSE 8501

# Jalankan Streamlit chatbot app
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
