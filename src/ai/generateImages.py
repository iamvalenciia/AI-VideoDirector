import base64
from pathlib import Path
from openai import OpenAI
from typing import Optional

def generate_transparent_square_image(prompt: str, output_directory: str, filename: Optional[str]) -> Path:
    """
    Genera una imagen cuadrada transparente usando gpt-image-1-mini y la guarda en el directorio especificado.

    Args:
        prompt (str): La descripción de la imagen deseada.
        output_directory (str): La ruta al directorio donde se guardará la imagen.
        filename (Optional[str]): El nombre del archivo para la imagen generada. Por defecto es "generated_image.png".

    Returns:
        Path: La ruta completa del archivo de imagen generado.
    """
    client = OpenAI()
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    full_filepath = output_path / filename

    try:
        # Generar la imagen con fondo transparente y tamaño cuadrado
        image_response = client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            n=1,
            size="1024x1024",  # Tamaño cuadrado
            background="transparent",  # Fondo transparente
            output_format="png",  # PNG soporta transparencia
        )

        # La respuesta para gpt-image-1 siempre devuelve base64
        if image_response.data and image_response.data[0].b64_json:
            b64_image = image_response.data[0].b64_json
            image_data = base64.b64decode(b64_image)

            with open(full_filepath, "wb") as f:
                f.write(image_data)
            print(f"Imagen generada y guardada en: {full_filepath.resolve()}")
            return full_filepath
        else:
            raise ValueError("No se pudo obtener la imagen generada del modelo.")

    except Exception as e:
        print(f"Error al generar la imagen: {e}")
        raise

