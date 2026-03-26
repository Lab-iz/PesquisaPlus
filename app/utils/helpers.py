import re
from datetime import UTC, datetime


def count_words(text):
    return len(re.findall(r"\b[\w-]+\b", text or ""))


def parse_tags(raw_value):
    if not raw_value:
        return []
    return [tag.strip() for tag in raw_value.split(",") if tag.strip()]


def normalize_multiline(text):
    return "\n".join(line.rstrip() for line in (text or "").splitlines()).strip()


def percentage(part, whole):
    if not whole:
        return 0
    return round((part / whole) * 100)


def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)
