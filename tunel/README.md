Rất hay! Dưới đây là hướng dẫn **tạo Cloudflare Tunnel** để mẹ bạn (hoặc bất kỳ ai) có thể truy cập vào **ứng dụng chạy trên máy bạn ở cổng `8501`** (ví dụ: Streamlit, FastAPI, v.v.).

---

## 🎯 Mục tiêu:

Cho phép truy cập máy bạn qua Internet bằng link như:

```
https://yourname-tunnel.trycloudflare.com
```

---

## ✅ Cách đơn giản nhất: **Cloudflare Tunnel không cần domain**

Cloudflare hỗ trợ chế độ **Quick Tunnel** — bạn không cần domain, chỉ cần chạy:

```bash
npx cloudflare tunnel --url http://localhost:8501
```

Hoặc nếu bạn đã cài Cloudflare CLI (`cloudflared`), thì:

```bash
cloudflared tunnel --url http://localhost:8501
```

Sau đó, bạn sẽ thấy dòng:

```
https://yourname-tunnel.trycloudflare.com
```

→ Gửi link này cho mẹ bạn là xong 🎉

---

## 🧰 Chi tiết từng bước

### 🔹 Bước 1: Cài `cloudflared`

#### Trên Ubuntu:

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 🔹 Bước 2: Chạy tunnel

```bash
cloudflared tunnel --url http://localhost:8501
```

(hoặc `cloudflared tunnel --url http://127.0.0.1:8501`)

Nó sẽ tạo một URL công khai như:

```
https://wise-mushroom-seal.trycloudflare.com
```

→ Bạn gửi link này cho mẹ bạn.

---

## ✅ Option nâng cao: dùng domain riêng (nếu bạn có)

Nếu bạn có domain riêng (VD: `mom.mydomain.com`), thì bạn có thể:

1. Đăng ký domain tại Cloudflare.
2. Cấu hình tunnel cố định bằng lệnh:

   ```bash
   cloudflared login
   cloudflared tunnel create mom-tunnel
   cloudflared tunnel route dns mom-tunnel mom.mydomain.com
   cloudflared tunnel run mom-tunnel
   ```

---

## ⚠️ Lưu ý khi chia sẻ tunnel

* Máy bạn **phải luôn mở tunnel** thì người khác mới truy cập được.
* Nếu bạn khởi động lại máy → cần chạy lại tunnel thủ công (hoặc cấu hình systemd để auto-run).
* Dữ liệu đi qua Cloudflare → an toàn hơn so với mở cổng router.

---

## 🧪 Kiểm tra

Sau khi chạy:

```bash
cloudflared tunnel --url http://localhost:8501
```

→ Mở thử link đó trên điện thoại bạn hoặc máy khác để đảm bảo mẹ bạn có thể truy cập được.

---

Bạn muốn làm cách thủ công (dùng domain riêng) hay nhanh gọn (tunnel tạm thời)? Mình có thể hỗ trợ cấu hình tự động hóa luôn nếu bạn dùng nó thường xuyên.

Bạn đã **nhấn `Ctrl+C`** để dừng tunnel, nên Cloudflare log báo:

```
INF Initiating graceful shutdown due to signal interrupt ...
ERR no more connections active and exiting
INF Tunnel server stopped
```

---

## ✅ Giải thích ngắn gọn:

* `^C`: bạn nhấn Ctrl+C → lệnh `cloudflared` bị dừng lại.
* Tunnel bị đóng, link **`https://truth-massachusetts-tablets-express.trycloudflare.com` không còn hoạt động** nữa.
* Không có lỗi gì nghiêm trọng cả — chỉ là bạn **dừng thủ công**.

---

## ✅ Nếu bạn muốn **giữ tunnel luôn chạy**, bạn có 3 lựa chọn:

---

### 🟢 **Cách 1: Dùng `tmux` để chạy nền**

```bash
sudo apt install tmux
tmux new -s tunnel
cloudflared tunnel --url http://localhost:8501
```

* Sau đó nhấn `Ctrl+B` rồi `D` để **thoát mà vẫn giữ tunnel chạy nền**
* Quay lại session:

```bash
tmux attach -t tunnel
```

---

### 🟢 **Cách 2: Dùng systemd (chạy tự động khi boot)**

Tạo file dịch vụ `/etc/systemd/system/cloudflared-tunnel.service`:

```ini
[Unit]
Description=Cloudflare Tunnel to expose Streamlit
After=network.target

[Service]
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8501
Restart=always
User=your-linux-user
WorkingDirectory=/home/your-linux-user
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

> Nhớ thay `/usr/local/bin/cloudflared` và `your-linux-user` phù hợp

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-tunnel
sudo systemctl start cloudflared-tunnel
```

---

### 🟢 **Cách 3: Dùng `nohup` (chạy 1 lần, không tắt khi logout)**

```bash
nohup cloudflared tunnel --url http://localhost:8501 > tunnel.log 2>&1 &
```

→ Tunnel sẽ chạy nền. Log lưu ở `tunnel.log`.

---

## ✅ Tổng kết

| Mục tiêu                | Cách làm                                 |
| ----------------------- | ---------------------------------------- |
| Giữ tunnel chạy lâu dài | Dùng `tmux`, `nohup` hoặc `systemd`      |
| Dừng = Ctrl+C           | Tunnel bị đóng, link mất                 |
| Muốn khởi động lại      | Chạy lại: `cloudflared tunnel --url ...` |

---

👉 Bạn muốn mình giúp cấu hình `tmux` hay `systemd` để mẹ bạn luôn truy cập được kể cả khi bạn logout/restart máy không? Mình có thể viết script tự động luôn cho bạn.
