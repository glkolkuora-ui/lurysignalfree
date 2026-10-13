FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV PORT=8080
ENV HOST=0.0.0.0
EXPOSE 8080
CMD ["python3", "server.py"]
