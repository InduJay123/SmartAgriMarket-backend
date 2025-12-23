import pandas as pd
from datetime import datetime
from apps.products.models import Crop, CropPrice

def process_price_file(upload_instance):
    try:
        file_path = upload_instance.file.path
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)

        for _, row in df.iterrows():
            crop, _ = Crop.objects.get_or_create(
                name=row['crop_name'],
                defaults={'category': 'Vegetable', 'season': 'All season', 'avg_price': row['price']}
            )

            CropPrice.objects.update_or_create(
                crop=crop,
                market=row['market'],
                date=row['date'],
                defaults={
                    'price': row['price'],
                    'unit': row['unit']
                }
            )

        upload_instance.status = 'processed'
        upload_instance.save()

    except Exception as e:
        upload_instance.status = 'failed'
        upload_instance.error_message = str(e)
        upload_instance.save()
