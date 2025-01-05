import qrcode
import json
from pathlib import Path
import logging
import os

class QRCodeGenerator:
    def __init__(self, base_dir="assets/qr_codes/"):
        self.base_dir = base_dir
        self.setup_logging()
        self._ensure_directory_exists()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='qr.log'
        )
        self.logger = logging.getLogger(__name__)

    def _ensure_directory_exists(self):
        """Ensure the QR codes directory exists"""
        try:
            Path(self.base_dir).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"QR code directory ensured at: {self.base_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create QR code directory: {str(e)}")
            raise

    def generate_product_qr(self, product):
        """
        Generate a QR code for a product and save it to the QR codes directory.
        
        Args:
            product: Product object containing product details
            
        Returns:
            str: Path to the generated QR code file
        """
        try:
            # Create QR code data dictionary
            qr_data = {
                "product_id": product.product_id,
                "name": product.name,
                "category": product.category,
                "price": str(product.price),
                "description": product.description
            }
            
            # Convert data to JSON string
            qr_content = json.dumps(qr_data)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)

            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Generate filename and save path
            filename = f"product_{product.product_id}.png"
            save_path = os.path.abspath(os.path.join(self.base_dir, filename))
            
            # Save QR code image
            qr_image.save(save_path)
            
            self.logger.info(f"QR code generated and saved at: {save_path}")
            return save_path

        except Exception as e:
            self.logger.error(f"Failed to generate QR code: {str(e)}")
            raise