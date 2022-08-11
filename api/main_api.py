from time import sleep

import requests

from api.api_utils import save_response_images_to_file_api

payload = {
    "task_type": "text2im",
    "prompt": {
        "caption": "Red panda on a skateboard, digital art, synthwave",
        "batch_size": 4,
    },
}

# For now auth_header is retrieved by hand from the web browser.
# In the web browser press Inspect then go to network recorder
# Launch generation of image
# Copy the Authentication header from the network recorder
# It should have "bearer" in it
# Paste it into the code below
auth_header: str = ""
# auth_header = "Bearer ************"
assert len(auth_header), "auth_header is not set"
assert "bearer" in auth_header.lower(), "bearer is not valid"
content_type = "application/json"
create_task_link = "https://labs.openai.com/api/labs/tasks"

headers = {
    "Content-type": content_type,
    "Authorization": auth_header,
}

if __name__ == "__main__":
    ret = requests.post(create_task_link, json=payload, headers=headers)
    ret = ret.json()
    sleep(5)
    while ret["status"] == "pending":
        ret = requests.get(create_task_link + "/" + ret["id"], headers=headers)
        ret = ret.json()
        sleep(5)
    if ret["status"] == "succeeded":
        save_response_images_to_file_api(ret)
print("DONE")
