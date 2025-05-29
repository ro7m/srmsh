def download_s3_file():
    # Create S3 client
    s3_client = boto3.client('s3')
    
    # Create local directory if it doesn't exist
    Path('/data').mkdir(parents=True, exist_ok=True)
    
    # Download the file
    s3_client.download_file(
        Bucket='your-bucket-name',        # Replace with your bucket
        Key='path/to/your/file.csv',      # Replace with your S3 key/path
        Filename='/data/local_file.csv'   # Local destination
    )
    print("File downloaded successfully!")
