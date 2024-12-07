# Chọn image cơ sở
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép tệp yêu cầu vào container
COPY requirements.txt .

# Cài đặt các phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Install curl
RUN apt-get update && apt-get install -y curl

# Sao chép mã nguồn vào container
COPY . .

# Copy the startup script into the container
COPY startup.sh /usr/local/bin/startup.sh

# Make the script executable
RUN chmod +x /usr/local/bin/startup.sh

# Set the entrypoint to the startup script
ENTRYPOINT ["/usr/local/bin/startup.sh"]

# Mở cổng cho ứng dụng (thay đổi theo cổng mà ứng dụng của bạn sử dụng)
EXPOSE 4006

# Lệnh chạy ứng dụng (thay đổi theo lệnh khởi động của bạn)
CMD ["python", "-u", "app.py"]