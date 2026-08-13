FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Create the upload and output folders
RUN mkdir -p uploads redacted
RUN chmod 777 uploads redacted

# Run gunicorn on port 7860 (Hugging Face default)
ENV PORT=7860
EXPOSE 7860

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860", "--workers", "1", "--threads", "2", "--timeout", "600"]
