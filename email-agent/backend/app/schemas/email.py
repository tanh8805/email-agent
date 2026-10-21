from pydantic import BaseModel, ConfigDict, Field


class EmailWebhookIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    thread_id: str | None = Field(default=None, alias="threadId")
    sender: str | None = Field(default=None, alias="from")
    to: str | list[str] | None = None
    subject: str | None = None
    body_text: str | None = None
    received_at: str | None = None


class EmailWebhookOut(BaseModel):
    status: str = "received"
    id: str
    thread_id: str | None = Field(default=None, serialization_alias="threadId")