import requests

def test_microservice():
    # API endpoint
    api_url = "http://localhost:5012/process"  

    # Test file path 
    test_file_path = "n4adj.txt"
    category = "adjectives"
    level = "N2"

    # Create a sample file for testing
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("悲しい : (かなしい) = sad\n")
        f.write("浅い : (あさい) = shallow\n")
        f.write("浅い ~ (あさい) # shallow\n")  # Invalid line

    # Process data
    with open(test_file_path, "rb") as file:
        files = {"file": file}
        data = {"category": category, "level": level}

        try:
            print(f"Uploading file: {test_file_path} to the microservice...")

            # Send the POST request
            response = requests.post(api_url, files=files, data=data)
            if response.ok:
                result = response.json()

                # Print the main response message
                print(f"Response: {result['message']}")

                # Check if a processed file is available
                if "processed_file_url" in result and result["processed_file_url"]:
                    processed_file_url = result["processed_file_url"]
                    print(f"Downloading processed file from {processed_file_url}...")
                    processed_file_response = requests.get(processed_file_url)
                    if processed_file_response.ok:
                        processed_file_name = "processed_file.txt"
                        with open(processed_file_name, "wb") as processed_file:
                            processed_file.write(processed_file_response.content)
                        print(f"Processed file saved as {processed_file_name}.")
                    else:
                        print("Failed to download the processed file.")

                # Check if an invalid words file is available
                if "invalid_file_url" in result and result["invalid_file_url"]:
                    invalid_file_url = result["invalid_file_url"]
                    print(f"Partial success. Downloading invalid words file from {invalid_file_url}...")
                    invalid_file_response = requests.get(invalid_file_url)
                    if invalid_file_response.ok:
                        invalid_file_name = "invalid_words.txt"
                        with open(invalid_file_name, "wb") as invalid_file:
                            invalid_file.write(invalid_file_response.content)
                        print(f"Invalid words file saved as {invalid_file_name}.")
                    else:
                        print("Failed to download the invalid words file.")

                # Handle full success without invalid lines
                if not result.get("invalid_file_url"):
                    print("Full success! No invalid words.")
            else:
                # Handle errors
                error_message = response.json().get("error", "An unknown error occurred.")
                print(f"Error: {error_message}")

        except Exception as e:
            print(f"An exception occurred: {str(e)}")

if __name__ == "__main__":
    test_microservice()
