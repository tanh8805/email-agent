# Email Agent

Agent xử lý email tự động. n8n lấy email từ Gmail / Outlook rồi gửi sang backend FastAPI. Backend dùng LangGraph để phân loại, tóm tắt và soạn nháp trả lời, sau đó lưu kết quả vào PostgreSQL.

## Công nghệ

- FastAPI + LangGraph (Python 3.12, quản lý bằng [uv](https://docs.astral.sh/uv/))
- PostgreSQL 16
- n8n

## Chạy bằng Docker

```bash
cp .env.example .env
cd infra
docker compose up -d --build
```

Các service đọc biến môi trường trực tiếp từ `.env` ở thư mục gốc qua `env_file`, nên không cần `--env-file`. Thiếu `.env` thì compose báo lỗi ngay.

| Service | URL / cổng |
| --- | --- |
| Backend (API docs) | http://localhost:8000/docs |
| n8n | http://localhost:5678 |
| PostgreSQL | localhost:5432 |

`infra/init.sql` chỉ chạy lần đầu khi volume Postgres còn trống. Muốn chạy lại, xoá volume:

```bash
cd infra && docker compose down -v
```

## Workflow n8n

Mở n8n, chọn **Import from file** và nạp `workflows/gmail-to-api.json` hoặc `workflows/outlook-to-api.json`. Sau đó cấu hình credential Gmail / Outlook trong n8n.

## Chạy local (không Docker)

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
