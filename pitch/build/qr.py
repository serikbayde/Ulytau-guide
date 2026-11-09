"""QR на бота в цветах презентации. Имя бота: из .env (BOT_USERNAME) или README (@yelulytaubot)."""
import os, pathlib, qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
ROOT = pathlib.Path(__file__).resolve().parents[2]
name = os.environ.get("BOT_USERNAME", "yelulytaubot").lstrip("@")
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=24, border=2)
q.add_data(f"https://t.me/{name}"); q.make(fit=True)
for tag, fg, bg in [("dark", (15, 27, 45), (247, 241, 230)), ("light", (15, 27, 45), (255, 255, 255))]:
    img = q.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(),
                       color_mask=SolidFillColorMask(back_color=bg, front_color=fg))
    img.save(ROOT / f"pitch/assets/qr_{tag}.png")
print(name)
