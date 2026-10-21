# Email Agent

Agent xử lý email tự động. n8n lấy email từ Gmail / Outlook rồi gửi sang backend FastAPI qua webhook. Backend lưu email vào PostgreSQL (có chống trùng) để agent LangGraph xử lý tiếp.

Trạng thái hiện tại: đã có webhook nhận và lưu email, endpoint kiểm tra sức khoẻ. Phần agent LangGraph (phân loại, tóm tắt, soạn nháp trả lời) đang phát triển.

## Công nghệ

- FastAPI, SQLAlchemy, LangGraph (Python 3.12, quản lý bằng [uv](https://docs.astral.sh/uv/))
- PostgreSQL 16
- n8n
- Docker Compose

## Cấu hình

```bash
cp .env.example .env
```

| Biến | Ý nghĩa |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Tài khoản và tên database của Postgres, backend cũng dùng các biến này |
| `DB_POSTGRESDB_USER`, `DB_POSTGRESDB_PASSWORD`, `DB_POSTGRESDB_DATABASE` | Để n8n kết nối cùng database. **Phải khớp** với 3 biến `POSTGRES_*` ở trên |
| `N8N_ENCRYPTION_KEY` | Khoá mã hoá credential của n8n. Tạo bằng `openssl rand -hex 24` và **giữ nguyên** sau khi n8n đã có credential |
| `TZ` | Múi giờ |

Các service đọc `.env` ở thư mục gốc qua `env_file`, nên không cần `--env-file`. Thiếu `.env` thì compose báo lỗi ngay.

## Chạy bằng Docker

```bash
cd infra
docker compose up -d --build
```

| Service | URL / cổng |
| --- | --- |
| Backend (API docs) | http://localhost:8000/docs |
| n8n | http://localhost:5678 |
| PostgreSQL | localhost:5432 |

Xem log (có in payload của mỗi request tới webhook):

```bash
docker logs -f backend
```

### Build lại sau khi sửa code

Chỉ build lại backend, **dữ liệu được giữ nguyên**:

```bash
cd infra
docker compose up -d --build backend
```

> **Không dùng `docker compose down -v`.** Cờ `-v` xoá volume, tức là mất toàn bộ dữ liệu Postgres. n8n lưu workflow và credential trong chính database này nên cũng mất theo. Muốn dừng stack thì dùng `docker compose stop` hoặc `docker compose down` (không có `-v`).

Nên sao lưu trước khi làm việc rủi ro:

```bash
docker exec postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql
```

### Đổi `.env` sau khi đã khởi tạo

Postgres chỉ đặt user và mật khẩu một lần, lúc tạo volume. Đổi `POSTGRES_PASSWORD` trong `.env` sau đó sẽ làm backend và n8n báo sai mật khẩu. Hãy đổi mật khẩu trong DB bằng `ALTER USER`, đừng xoá volume.

## API

### `GET /health`

Kiểm tra kết nối database. Trả `200 {"status": "ok", "database": "up"}`, hoặc `503` khi DB không kết nối được.

### `POST /webhook/email`

Nhận email từ n8n và lưu vào database.

| Trường | Bắt buộc | Mô tả |
| --- | --- | --- |
| `id` | có | ID email từ nhà cung cấp |
| `provider` | không | `gmail` (mặc định) hoặc `outlook` |
| `account` | không | Địa chỉ mailbox nhận email, mặc định rỗng |
| `threadId` | không | ID luồng hội thoại |
| `from` | không | Người gửi |
| `to` | không | Người nhận: chuỗi (`"A <a@x.com>, b@y.com"`) hoặc danh sách |
| `subject` | không | Tiêu đề |
| `body_text` | không | Nội dung dạng text |
| `received_at` | không | Thời điểm nhận: ISO 8601, epoch (giây hoặc mili giây) hoặc RFC 2822. Thiếu hoặc không đọc được thì dùng giờ hiện tại |

Trường không có trong bảng trên bị bỏ qua. Thiếu trường không bắt buộc thì không lỗi.

```bash
curl -X POST http://localhost:8000/webhook/email \
  -H 'Content-Type: application/json' \
  -d '{"id": "18c1", "threadId": "t1", "from": "Alice <a@x.com>", "to": "b@y.com", "subject": "Hi", "body_text": "hello"}'
```

Phản hồi `200`:

```json
{"status": "received", "id": "18c1", "threadId": "t1"}
```

Email đã có thì vẫn trả `200` với `"status": "duplicate"` và không lưu thêm. Mã khác: `422` nếu thiếu `id` hoặc `provider` không hợp lệ, `503` nếu lỗi database (n8n có thể retry).

## Database

Bảng `emails` được tạo bởi `infra/init.sql` khi volume Postgres còn trống.

Chống trùng bằng ràng buộc `UNIQUE (provider, account, external_id)`. ID email của Gmail và Outlook chỉ duy nhất trong từng mailbox, nên phạm vi chống trùng gồm cả provider và account. Khi kết nối nhiều mailbox, hãy để n8n gửi địa chỉ mailbox vào trường `account`.

`init.sql` chỉ chạy một lần. Khi đổi schema, sửa `init.sql` cho project mới và chạy `ALTER TABLE` thủ công trên database đang dùng. Hiện chưa có công cụ migration.

## Workflow n8n

Workflow n8n gọi webhook tại `http://backend:8000/webhook/email` (n8n và backend cùng mạng Docker). Các file `workflows/gmail-to-api.json` và `workflows/outlook-to-api.json` hiện còn trống. Khi có nội dung, vào n8n chọn **Import from file** rồi cấu hình credential Gmail / Outlook.

## Chạy local (không Docker)

Cần một Postgres đang chạy (ví dụ container `postgres` ở trên) và `.env` ở thư mục gốc.

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

## Test

```bash
cd backend
uv run pytest
```
