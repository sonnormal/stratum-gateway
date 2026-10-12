import unicodedata

from gateway.ingress.mime_parser import ParsedEmail

KNOWN_BANK_DOMAINS = (
    "vib.com.vn",
    "vietcombank.com.vn",
    "techcombank.com.vn",
    "mbbank.com.vn",
)

DISCARD_SENDERS = (
    "marketing.",
    "promo.",
    "newsletter.",
)

TRANSACTION_KEYWORDS = (
    # Vietnamese unaccented
    "bien dong",
    "so du",
    "giao dich",
    "thanh toan",
    "chuyen tien",
    "hoa don",
    # Vietnamese accented
    "biến động",
    "số dư",
    "giao dịch",
    "thanh toán",
    "chuyển tiền",
    "hóa đơn",
    # English
    "alert",
    "balance",
    "debit",
    "credit",
    "transaction",
)


def strip_diacritics(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    cleaned = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return cleaned.replace("đ", "d").replace("Đ", "D")


def is_bank_transaction_email(email: ParsedEmail) -> bool:
    sender_lower = email.sender.lower()
    subject_lower = email.subject.lower()
    subject_stripped = strip_diacritics(subject_lower)

    if any(m in sender_lower for m in DISCARD_SENDERS):
        return False

    matches_domain = any(domain in sender_lower for domain in KNOWN_BANK_DOMAINS)
    matches_keyword = any(
        kw in subject_lower or kw in subject_stripped for kw in TRANSACTION_KEYWORDS
    )

    return matches_domain and matches_keyword
