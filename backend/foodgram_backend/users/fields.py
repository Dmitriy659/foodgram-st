import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework.fields import ImageField
from rest_framework.exceptions import ValidationError


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                header, base64_data = data.split(";base64,")
                file_ext = header.split("/")[-1]  # расширение
                decoded_file = base64.b64decode(base64_data)

                file_name = f"{uuid.uuid4()}.{file_ext}"
                complete_file = ContentFile(decoded_file, name=file_name)

                return super().to_internal_value(complete_file)
            except Exception:
                raise ValidationError("Невозможно декодировать изображение.")
        return super().to_internal_value(data)
