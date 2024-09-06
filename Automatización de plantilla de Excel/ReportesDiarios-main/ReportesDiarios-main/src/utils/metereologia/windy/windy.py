import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
import os

async def take_screenshot_and_edit(estacion, lat, long):
    # Configuración inicial con Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"https://www.windy.com/{lat}/{long}", timeout=50000)
        await asyncio.sleep(3)  # Espera para asegurar que la página cargue completamente
        await page.screenshot(path="screenshot.png")
        await browser.close()

    # Cargar y editar la imagen
    with Image.open("screenshot.png") as img:
        # Recortar la imagen
        left, top, right, bottom = 0, 500, 1280, 685
        cropped_img = img.crop((left, top, right, bottom))
        
        # Dibujar en la imagen recortada
        draw = ImageDraw.Draw(cropped_img)
        draw.rectangle([(0, 0), (100, 25)], fill=(248, 248, 248))
        
        # Guardar la imagen editada
        cropped_img.save(f"windy.png")
    
    # Opcional: Eliminar la imagen original si se desea
    os.remove("screenshot.png")

# Variables de ejemplo
estacion = 'Calenturitas'
lat = 9.67412134
long = -73.47385574

# Ejecutar la función asíncrona
if __name__ == "__main__":
    asyncio.run(take_screenshot_and_edit(estacion, lat, long))
