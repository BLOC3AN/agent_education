# 🚀 AWS Free Tier Deployment Guide

Hướng dẫn triển khai Agent Education Platform lên AWS Free Tier với tối ưu hóa tài nguyên.

## 📋 Tổng quan

Phiên bản này được tối ưu hóa đặc biệt cho AWS Free Tier (EC2 t2.micro) với:
- **RAM**: 1GB (sử dụng tối đa 800MB, để lại 200MB cho hệ thống)
- **CPU**: 1 vCPU (sử dụng tối đa 0.8 vCPU)
- **Storage**: 30GB EBS (Free Tier)
- **Network**: 15GB data transfer/tháng

## 🎯 Tối ưu hóa đã thực hiện

### 1. **Docker Image Optimization**
- ✅ Multi-stage build để giảm kích thước image
- ✅ Sử dụng Alpine Linux (nhẹ hơn 80% so với Ubuntu)
- ✅ Chỉ cài đặt dependencies cần thiết
- ✅ Loại bỏ build tools khỏi runtime image

### 2. **Resource Limits**
- ✅ Giới hạn RAM: 800MB (để lại 200MB cho OS)
- ✅ Giới hạn CPU: 0.8 vCPU
- ✅ Tối ưu hóa logging (10MB max, 3 files)
- ✅ Health check tần suất thấp (60s interval)

### 3. **Dependencies Optimization**
- ✅ Loại bỏ `langchain` đầy đủ, chỉ dùng `langchain-core`
- ✅ Loại bỏ Google API dependencies không cần thiết
- ✅ Sử dụng `orjson` thay vì `json` (nhanh hơn)
- ✅ Thêm `loguru` cho logging hiệu quả

### 4. **External Services**
- ✅ Sử dụng **Qdrant Cloud** thay vì chạy Qdrant local
- ✅ Loại bỏ Kafka, Zookeeper (không cần thiết cho Free Tier)
- ✅ Redis optional (có thể bật nếu cần)

## 🛠️ Yêu cầu hệ thống

### AWS EC2 Instance
- **Instance Type**: t2.micro (Free Tier eligible)
- **OS**: Ubuntu 20.04 LTS hoặc Amazon Linux 2
- **Storage**: 30GB gp2 EBS volume
- **Security Group**: Mở port 8501 (HTTP), 22 (SSH)

### Software Requirements
```bash
# Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

## 📦 Cài đặt và Triển khai

### Bước 1: Chuẩn bị EC2 Instance

1. **Tạo EC2 Instance**:
   - Chọn t2.micro (Free Tier)
   - Ubuntu 20.04 LTS
   - 30GB gp2 storage
   - Tạo key pair mới hoặc sử dụng existing

2. **Cấu hình Security Group**:
   ```
   Type: SSH, Port: 22, Source: Your IP
   Type: Custom TCP, Port: 8501, Source: 0.0.0.0/0
   ```

3. **Kết nối SSH**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```

### Bước 2: Cài đặt Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Install Git
sudo apt install git -y

# Logout and login again to apply docker group
exit
# SSH lại
```

### Bước 3: Clone và Setup Project

```bash
# Clone repository
git clone <your-repo-url>
cd agent_education

# Copy và cấu hình environment file
cp aws/.env.aws aws/.env.aws.local
nano aws/.env.aws.local
```

### Bước 4: Cấu hình Environment

Chỉnh sửa file `aws/.env.aws.local`:

```bash
# Qdrant Cloud (REQUIRED)
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=agent_education

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key

# Security
SECRET_KEY=your-random-secret-key-here
```

### Bước 5: Deploy Application

```bash
# Make scripts executable
chmod +x aws/deploy.sh aws/entrypoint.sh

# Deploy application
./aws/deploy.sh deploy
```

## 🔧 Quản lý Application

### Các lệnh cơ bản

```bash
# Deploy/Start application
./aws/deploy.sh deploy

# Xem logs
./aws/deploy.sh logs

# Xem status và resource usage
./aws/deploy.sh status

# Stop application
./aws/deploy.sh stop

# Restart application
./aws/deploy.sh restart

# Cleanup (stop và xóa containers)
./aws/deploy.sh cleanup

# Xem help
./aws/deploy.sh help
```

### Monitoring

```bash
# Xem resource usage real-time
docker stats

# Xem logs real-time
docker-compose -f aws/docker-compose.yml logs -f

# Xem system resources
htop
free -h
df -h
```

## 🌐 Qdrant Cloud Setup

### Tạo Qdrant Cloud Account

1. **Đăng ký tài khoản**:
   - Truy cập: https://cloud.qdrant.io
   - Đăng ký tài khoản miễn phí
   - Xác thực email

2. **Tạo Cluster**:
   - Chọn "Create Cluster"
   - Chọn Free Tier (1GB storage)
   - Chọn region gần nhất (Singapore cho VN)
   - Đặt tên cluster: `agent-education`

3. **Lấy thông tin kết nối**:
   - URL: `https://your-cluster-id.qdrant.io`
   - API Key: Tạo trong phần "API Keys"

### Cấu hình trong .env.aws

```bash
QDRANT_URL=https://your-cluster-id.qdrant.io
QDRANT_API_KEY=your-api-key-here
QDRANT_COLLECTION_NAME=agent_education
```

## 🔒 Security Best Practices

### 1. **EC2 Security**
```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8501

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

### 2. **Application Security**
- ✅ Sử dụng non-root user trong container
- ✅ Giới hạn resource usage
- ✅ Secure environment variables
- ✅ Regular security updates

### 3. **API Keys Management**
- ✅ Không commit API keys vào git
- ✅ Sử dụng environment variables
- ✅ Rotate keys định kỳ
- ✅ Giới hạn permissions cho keys

## 📊 Performance Tuning

### 1. **Memory Optimization**
```bash
# Thêm swap file (nếu cần)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. **Docker Optimization**
```bash
# Cleanup unused images/containers
docker system prune -f

# Limit log size
echo '{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

### 3. **Application Tuning**
- ✅ Lightweight mode enabled
- ✅ Reduced upload/message sizes
- ✅ Optimized health checks
- ✅ Efficient logging

## 🚨 Troubleshooting

### Common Issues

#### 1. **Out of Memory**
```bash
# Check memory usage
free -h
docker stats

# Solutions:
# - Add swap file
# - Reduce container memory limits
# - Enable lightweight mode
```

#### 2. **Container Won't Start**
```bash
# Check logs
./aws/deploy.sh logs

# Common causes:
# - Missing environment variables
# - Port conflicts
# - Insufficient resources
```

#### 3. **Application Slow**
```bash
# Check resource usage
htop
docker stats

# Solutions:
# - Optimize queries
# - Use caching
# - Reduce concurrent requests
```

#### 4. **Qdrant Connection Issues**
```bash
# Test connection
curl -X GET "https://your-cluster.qdrant.io/collections" \
  -H "api-key: your-api-key"

# Common causes:
# - Wrong URL/API key
# - Network issues
# - Cluster not running
```

## 💰 Cost Optimization

### Free Tier Limits
- **EC2**: 750 hours/month t2.micro
- **EBS**: 30GB storage
- **Data Transfer**: 15GB/month
- **Qdrant Cloud**: 1GB storage free

### Tips để tiết kiệm
1. **Stop instance khi không dùng**:
   ```bash
   # Stop EC2 instance (giữ EBS)
   aws ec2 stop-instances --instance-ids i-1234567890abcdef0
   ```

2. **Monitor usage**:
   - AWS CloudWatch
   - Billing alerts
   - Resource usage tracking

3. **Optimize resources**:
   - Cleanup unused Docker images
   - Monitor memory/CPU usage
   - Use external services (Qdrant Cloud)

## 📈 Scaling Options

### Khi cần scale up:

1. **Vertical Scaling**:
   - Upgrade to t3.small (2GB RAM)
   - Add more EBS storage

2. **Horizontal Scaling**:
   - Load balancer + multiple instances
   - Container orchestration (ECS/EKS)

3. **Managed Services**:
   - AWS App Runner
   - AWS Fargate
   - AWS Lambda (serverless)

## 🔄 Backup & Recovery

### 1. **Data Backup**
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Upload to S3 (if configured)
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/
```

### 2. **EBS Snapshots**
```bash
# Create snapshot via AWS CLI
aws ec2 create-snapshot --volume-id vol-1234567890abcdef0 --description "Daily backup"
```

### 3. **Configuration Backup**
- Backup `.env.aws` file
- Backup custom configurations
- Document any manual changes

## 📞 Support

### Resources
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Docker Documentation**: https://docs.docker.com/
- **Qdrant Documentation**: https://qdrant.tech/documentation/

### Community
- AWS Free Tier Forum
- Docker Community
- Qdrant Discord

---

## 🎉 Kết luận

Với setup này, bạn có thể chạy Agent Education Platform trên AWS Free Tier một cách hiệu quả với:

- ✅ **Chi phí**: $0/tháng (trong giới hạn Free Tier)
- ✅ **Performance**: Tối ưu cho 1GB RAM
- ✅ **Reliability**: Health checks và auto-restart
- ✅ **Security**: Best practices applied
- ✅ **Scalability**: Dễ dàng scale khi cần

**Happy Deploying! 🚀**
