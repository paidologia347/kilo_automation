def run_pipeline() -> None:
    try:
        print("PIPELINE START")

        print("STEP 1: GENERATE PROMPTS")
        prompts = ["test image microstock"]
        print(f"STEP 1 COMPLETE: {len(prompts)} PROMPTS")

        print("STEP 2: GENERATE IMAGE")
        from PIL import Image
        import os

        os.makedirs("output", exist_ok=True)
        image_path = "output/test.jpg"
        img = Image.new("RGB", (512, 512), color=(255, 0, 0))
        img.save(image_path)
        print("IMAGE CREATED:", image_path)
        print("STEP 2 COMPLETE")

        print("STEP 3: UPSCALE (SKIP OR MOCK)")
        print("STEP 3 COMPLETE: SKIPPED")

        print("STEP 4: METADATA (SKIP OR MOCK)")
        print("STEP 4 COMPLETE: SKIPPED")

        print("STEP 5: UPLOAD")
        from utils.uploader import upload_file

        upload_success = upload_file(image_path)
        if upload_success:
            print("UPLOAD SUCCESS")
        else:
            print("UPLOAD FAILED")
        print("STEP 5 COMPLETE")

        print("PIPELINE DONE")

    except Exception as e:
        print("PIPELINE ERROR:", str(e))
