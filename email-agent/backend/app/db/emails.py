from datetime import datetime, timezone
from email.utils import getaddresses, parsedate_to_datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

INSERT_EMAIL = text(
    """
    INSERT INTO emails (
        provider, account, external_id, thread_id, sender,
        to_addresses, subject, body_text, received_at
    )
    VALUES (
        :provider, :account, :external_id, :thread_id, :sender,
        :to_addresses, :subject, :body_text, :received_at
    )
    ON CONFLICT (provider, account, external_id) DO NOTHING
    RETURNING id
    """
)


def parse_addresses(value: str | list[str] | None) -> list[str]:
    """Tách chuỗi 'A <a@x.com>, b@y.com' (hoặc list) thành danh sách địa chỉ."""
    if not value:
        return []
    raw = [value] if isinstance(value, str) else value
    return [addr for _, addr in getaddresses(raw) if addr]


def parse_received_at(value: str | None) -> datetime:
    """Đọc ISO 8601, epoch (giây/mili giây) hoặc RFC 2822; không đọc được thì dùng giờ hiện tại."""
    if value:
        value = value.strip()
        parsed = None
        try:
            if value.isdigit():
                ts = int(value)
                parsed = datetime.fromtimestamp(ts / 1000 if ts > 10**11 else ts, tz=timezone.utc)
            else:
                parsed = datetime.fromisoformat(value)
        except ValueError:
            try:
                parsed = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                parsed = None
        if parsed is not None:
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def save_email(
    db: Session,
    *,
    provider: str,
    account: str,
    external_id: str,
    thread_id: str | None,
    sender: str | None,
    to: str | list[str] | None,
    subject: str | None,
    body_text: str | None,
    received_at: str | None,
) -> UUID | None:
    row = db.execute(
        INSERT_EMAIL,
        {
            "provider": provider,
            "account": account,
            "external_id": external_id,
            "thread_id": thread_id,
            "sender": sender,
            "to_addresses": parse_addresses(to),
            "subject": subject,
            "body_text": body_text,
            "received_at": parse_received_at(received_at),
        },
    ).first()
    db.commit()
    return row[0] if row else None
