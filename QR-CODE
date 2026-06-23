from pyrogram import Client
from pyrogram.raw.functions.auth import ExportLoginToken
import qrcode
import base64

API_ID = 32816018
API_HASH = "73aa5abdd997d8dc991c261b010adfdf"

app = Client("userbot", api_id=API_ID, api_hash=API_HASH)

with app:
    token = app.invoke(
        ExportLoginToken(
            api_id=API_ID,
            api_hash=API_HASH,
            except_ids=[]
        )
    )

    qr_data = base64.b64encode(token.token).decode()

    qr = qrcode.QRCode()
    qr.add_data(qr_data)
    qr.make()

    print("\nСканируй этот QR в Telegram → Настройки → Устройства → Подключить устройство:\n")
    qr.print_ascii()
