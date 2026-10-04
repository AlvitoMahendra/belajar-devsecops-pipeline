FROM python:3.10-slim

WORKDIR /app

# Membuat user non-root
RUN useradd -m appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Memberikan kepemilikan aplikasi kepada appuser
RUN chown -R appuser:appuser /app

# Menjalankan aplikasi sebagai user non-root
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]