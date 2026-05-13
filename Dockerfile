# 1. Base Image
FROM python:3.11-slim

# 2. Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Working Directory
WORKDIR /app

# 4. System Dependencies
# Only run this once to keep the image slim
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Python Dependencies
# Install setuptools first for Python 3.13 compatibility
RUN pip install --no-cache-dir setuptools

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Project Code
COPY . /app/

# 7. Final Polish
EXPOSE 8000

# IMPORTANT: Ensure 'buddy_script' matches your project folder name!
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "buddy_script.wsgi:application"]