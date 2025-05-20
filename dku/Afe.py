import requests

# URL of your service in Kubernetes
service_url = "http://my-internal-service.default-api.svc.cluster.local:8080/your-endpoint"

# Form data to send
form_data = {
    "username": "user123",
    "password": "securepassword",
    "grant_type": "password",
    "client_id": "my-client"
}

# Headers specifying content type
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Make the POST request with form-encoded data
response = requests.post(
    service_url,
    data=form_data,  # requests will automatically form-encode this dictionary
    headers=headers
)

# Process the response
if response.status_code == 200:
    print("Success:", response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)
