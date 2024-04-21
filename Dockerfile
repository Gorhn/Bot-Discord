FROM python:3.10-bullseye
FROM gorialis/discord.py
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "src/main.py"]