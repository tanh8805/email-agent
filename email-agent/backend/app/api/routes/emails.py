from fastapi import APIRouter

from app.schemas.email import EmailWebhookIn, EmailWebhookOut

router = APIRouter(prefix="/webhook")


@router.post("/email", response_model=EmailWebhookOut, response_model_by_alias=True)
def receive_email(payload: EmailWebhookIn):
    return EmailWebhookOut(id=payload.id, thread_id=payload.thread_id)
