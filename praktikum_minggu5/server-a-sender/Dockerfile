FROM python:3.11-slim
WORKDIR /app
RUN pip install grpcio grpcio-tools
COPY . .
CMD ["python", "main.py"]