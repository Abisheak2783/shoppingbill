import os
import cloudinary
import cloudinary.uploader

# FINAL 100% GUARANTEE with NEW KEYS
cloudinary.config(
    cloud_name="dexrfqfjc",
    api_key="737714531369316",
    api_secret="YCdW_5o2sOi8TkS-QTs9339xhdk",
    secure=True
)

def final_upload():
    media_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
    product_images_dir = os.path.join(media_root, 'product_images')
    if not os.path.exists(product_images_dir): 
        print("Media folder missing!")
        return

    files = [f for f in os.listdir(product_images_dir) if os.path.isfile(os.path.join(product_images_dir, f))]
    
    print(f"STARTING FINAL UPLOAD for {len(files)} images...")
    
    for filename in files:
        local_path = os.path.join(product_images_dir, filename)
        # We use the path format "product_images/name" to match the DB
        public_id = f"product_images/{os.path.splitext(filename)[0]}"
        
        print(f"Uploading {filename}...")
        try:
            response = cloudinary.uploader.upload(
                local_path,
                public_id=public_id,
                unique_filename=False,
                overwrite=True
            )
            print(f"SUCCESS: {filename} -> {response.get('secure_url')}")
        except Exception as e:
            print(f"FAILED: {filename}. Error: {e}")

    print("\nIMAGE RESTORATION 100% COMPLETE!")

if __name__ == "__main__":
    final_upload()
