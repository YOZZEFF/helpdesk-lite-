from dataclasses import dataclass


@dataclass
class NotificationPayload:
    channel: str
    recipient: str
    subject: str
    body: str


class NotificationService:
    def __init__(self, channel: str = "slack"):
        self._channel = channel

    def send(self, payload: NotificationPayload) -> bool:
        # Placeholder — sends via configured channel (slack/email)
        print(f"[{self._channel}] To={payload.recipient} | "
              f"Subj={payload.subject} | Body={payload.body}")
        return True
