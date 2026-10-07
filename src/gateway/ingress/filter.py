from gateway.ingress.mime_parser import ParsedEmail

KNOWN_BANK_DOMAINS = (
    "vib.com.vn",
    "vietcombank.com.vn",
    "techcombank.com.vn",
    "mbbank.com.vn",
)

TRANSACTION_KEYWORDS = (
    "bien dong",
    "so du",
    "giao dich",
    "thanh toan",
    "alert",
    "balance",
    "debit",
    "credit",
)


def is_bank_transaction_email(email: ParsedEmail) -> bool:
    sender_lower = email.sender.lower()
    subject_lower = email.subject.lower()

    matches_domain = any(domain in sender_lower for domain in KNOWN_BANK_DOMAINS)
    matches_keyword = any(kw in subject_lower for kw in TRANSACTION_KEYWORDS)

    return matches_domain and matches_keyword
