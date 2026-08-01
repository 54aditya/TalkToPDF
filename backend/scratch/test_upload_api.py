import requests
import time

url = "http://localhost:8000/api/v1/documents/upload"
files = {"file": ("sample.pdf", open("sample.pdf", "rb"), "application/pdf")}

print("Uploading sample.pdf...")
response = requests.post(url, files=files)
if response.status_code == 202:
    data = response.json()
    doc_id = data["document"]["_id"]
    print(f"Upload successful! Document ID: {doc_id}")
    
    # Poll status
    for i in range(10):
        time.sleep(2)
        doc_resp = requests.get(f"http://localhost:8000/api/v1/documents/{doc_id}")
        if doc_resp.status_code == 200:
            doc_data = doc_resp.json()
            status = doc_data["status"]
            print(f"Poll {i+1}: Status = {status}")
            if status == "processed":
                print("SUCCESS: PDF parsing, embeddings generation, and Qdrant indexing completed!")
                print(f"Summary: {doc_data.get('summary')}")
                break
            elif status == "failed":
                print("FAILURE: Document parsing failed. Check celery worker logs.")
                break
        else:
            print(f"Failed to fetch status: {doc_resp.status_code}")
            break
else:
    print(f"Upload failed: {response.status_code} - {response.text}")
