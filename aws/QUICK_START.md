# ⚡ Quick Start - AWS Free Tier Deployment

## 🚀 Deploy trong 5 phút

### Bước 1: Chuẩn bị EC2 Instance
```bash
# Tạo EC2 t2.micro với Ubuntu 20.04
# Mở port 22 (SSH) và 8501 (HTTP)
# SSH vào instance
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Bước 2: Cài đặt Docker
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose git -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
# Logout và login lại
```

### Bước 3: Clone và Setup
```bash
git clone <your-repo-url>
cd agent_education
cp aws/.env.aws aws/.env.aws.local
nano aws/.env.aws.local  # Cấu hình API keys
```

### Bước 4: Deploy
```bash
chmod +x aws/deploy.sh aws/entrypoint.sh
./aws/deploy.sh deploy
```

### Bước 5: Truy cập
```
http://your-ec2-public-ip:8501
```

## 🔧 Quản lý nhanh

```bash
# Xem status
./aws/deploy.sh status

# Xem logs
./aws/deploy.sh logs

# Restart
./aws/deploy.sh restart

# Stop
./aws/deploy.sh stop
```

## 📋 Checklist

- [ ] EC2 t2.micro đã tạo
- [ ] Security Group mở port 8501
- [ ] Docker đã cài đặt
- [ ] Repository đã clone
- [ ] File .env.aws.local đã cấu hình
- [ ] Qdrant Cloud account đã tạo
- [ ] Application đã deploy thành công

## 🆘 Troubleshooting nhanh

**Container không start?**
```bash
./aws/deploy.sh logs
```

**Out of memory?**
```bash
free -h
docker stats
```

**Qdrant connection error?**
- Kiểm tra QDRANT_URL và QDRANT_API_KEY trong .env.aws.local

**Port 8501 không accessible?**
- Kiểm tra Security Group có mở port 8501 không

---

📖 **Chi tiết đầy đủ**: Xem `aws/README.md`
