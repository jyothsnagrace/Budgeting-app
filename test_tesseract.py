"""Test if Tesseract OCR is installed"""
import pytesseract
from PIL import Image

print('✓ pytesseract imported successfully')
print('Checking for Tesseract executable...')

try:
    # Try to set Windows path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    version = pytesseract.get_tesseract_version()
    print(f'✓ Tesseract OCR is installed: v{version}')
    print('\nReceipt parsing will work!')
except Exception as e:
    print(f'✗ Tesseract OCR not found: {e}')
    print('\n📥 To install Tesseract OCR:')
    print('   Windows: https://github.com/UB-Mannheim/tesseract/wiki')
    print('   Download and run the installer')
    print('\n💡 Alternative: Type receipt details manually in the text input')
