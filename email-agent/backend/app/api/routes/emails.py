import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.db.emails import save_email
from app.schemas.email import EmailWebhookIn, EmailWebhookOut

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/webhook")


@router.post("/email", response_model=EmailWebhookOut, response_model_by_alias=True)
def receive_email(payload: EmailWebhookIn, db: Session = Depends(get_db)):
    logger.info("POST /webhook/email payload: %s", payload.model_dump_json(by_alias=True, indent=2))
    try:
        email_id = save_email(
            db,
            provider=payload.provider,
            account=payload.account,
            external_id=payload.id,
            thread_id=payload.thread_id,
            sender=payload.sender,
            to=payload.to,
            subject=payload.subject,
            body_text=payload.body_text,
            received_at=payload.received_at,
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=503, detail="database unavailable")

    return EmailWebhookOut(
        status="received" if email_id else "duplicate",
        id=payload.id,
        thread_id=payload.thread_id,
    )
