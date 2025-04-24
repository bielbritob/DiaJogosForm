from datetime import datetime
import config as secret


def generate_pix_payload(reg_id: int, version: int, amount: float):
    def tlv(id_: str, value: str):
        return f"{id_}{len(value):02d}{value}"

    txid = f"ADV{reg_id:04d}-V{version}-{int(datetime.now().timestamp())}"

    payload = ''.join([
        tlv("00", "01"),
        tlv("26", tlv("00", "br.gov.bcb.pix") + tlv("01", secret.PIX_KEY)),
        tlv("52", "0000"),
        tlv("53", "986"),
        tlv("54", f"{amount:.2f}"),
        tlv("58", "BR"),
        tlv("59", secret.MERCHANT_NAME[:25]),
        tlv("60", secret.MERCHANT_CITY[:15]),
        tlv("62", tlv("05", txid))
    ])

    crc = 0xFFFF
    for b in payload.encode('utf-8'):
        crc ^= b << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF

    return payload + f"6304{crc:04X}"