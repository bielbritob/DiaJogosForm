import qrcode
from io import BytesIO
from datetime import datetime
from config import PIX_KEY, MERCHANT_CITY, MERCHANT_NAME

def generate_pix_payload(amount: float) -> str:
    def tlv(id_: str, value: str) -> str:
        return f"{id_}{len(value):02d}{value}"

    payload = tlv("00", "01")
    mai  = tlv("00", "br.gov.bcb.pix") + tlv("01", PIX_KEY)
    payload += tlv("26", mai)
    payload += tlv("52", "0000")
    payload += tlv("53", "986")
    payload += tlv("54", f"{amount:.2f}")
    payload += tlv("58", "BR")
    payload += tlv("59", MERCHANT_NAME[:25])
    payload += tlv("60", MERCHANT_CITY[:15])
    txid = datetime.now().strftime("%Y%m%d%H%M%S")
    payload += tlv("62", tlv("05", txid))

    def crc16(s: bytes) -> str:
        poly, reg = 0x1021, 0xFFFF
        for b in s:
            reg ^= b << 8
            for _ in range(8):
                reg = (reg << 1) ^ poly if (reg & 0x8000) else reg << 1
                reg &= 0xFFFF
        return f"{reg:04X}"

    payload += "6304" + crc16(payload.encode("utf-8"))
    return payload

def generate_qrcode(payload: str) -> BytesIO:
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf
