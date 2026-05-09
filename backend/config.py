import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://localhost:5432/helpdesk_lite"
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
    SLA_BREACH_NOTIFICATION_CHANNEL = os.getenv(
        "SLA_NOTIFICATION_CHANNEL", "slack"
    )
    ESCALATION_COOLDOWN_MINUTES = int(os.getenv("ESCALATION_COOLDOWN", 30))
