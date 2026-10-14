FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install grpcio grpcio-tools
COPY . .
CMD ["python", "main.py"]