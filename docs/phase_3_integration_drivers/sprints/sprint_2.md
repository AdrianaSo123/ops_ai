# 🔵 Sprint 2 — Gmail Integration

**Goal:** Implement the first real-world communication driver using the Gmail SMTP protocol.

---

## 🛠️ Tasks

- [ ] **Gmail Driver Implementation**:
    - Build `GmailDriver` in `opsai/core/drivers/communication/gmail.py`.
    - Implement authentication using SMTP and "App Passwords."
- [ ] **Translation Layer**:
    - Map `COMMUNICATION` payloads to standard SMTP fields (Subject, Body, To).
- [ ] **Sensitive Data Masking**:
    - Implement a `sanitize()` method to ensure email bodies are masked in snapshots if they contain recognized sensitive tokens.
- [ ] **Configuration**:
    - Add `OPSAI_DRIVER_GMAIL_USER` and `OPSAI_DRIVER_GMAIL_PASS` to `.env`.

---

## 📦 Definition of Done

- [ ] `check_health()` successfully verifies the SMTP handshake.
- [ ] Test email sent successfully to a development mailbox.
- [ ] Snapshot logs verify that sensitive content is masked.
