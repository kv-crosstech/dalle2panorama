import requests


def save_response_images_to_file_api(response: dict):
    """
    download image by link and save to disk with prompt + id
    status is guaranteed to be 'succeeded'
    """
    assert (
        response["status"] == "succeeded"
    ), "task response status is not 'succeeded'"
    images_urls = [
        x["generation"]["image_path"] for x in response["generations"]["data"]
    ]
    for i, image_url in enumerate(images_urls):
        print(f"saving image {i+1}")
        img_data = requests.get(image_url).content
        with open(
            f'{response["prompt"]["prompt"]["caption"]}_{i+1}.png', "wb"
        ) as f:
            f.write(img_data)
