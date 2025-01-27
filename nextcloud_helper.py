import os
import config
from nc_py_api import Nextcloud

nc = Nextcloud(
    nextcloud_url = config.NEXTCLOUD_URL, 
    nc_auth_user = config.NEXTCLOUD_USER, 
    nc_auth_pass = config.NEXTCLOUD_PASSWORD
    )
folder_path = '/chat_bridge_cache'

def upload_to_nextcloud(file):

    file_name = os.path.basename(file)
    dest_path = os.path.join(folder_path, file_name)
    with open(file, 'rb') as file_data:
        file_object = nc.files.upload_stream(
            path = dest_path,
            fp = file_data
            )
    return file_object.user_path
        
def create_share_link(file_path):

    share_info = nc.files.sharing.create(        
        path=file_path,
        share_type=3
        )
    if share_info:
        print(f"Created share link: {share_info.url}")
        return share_info.url
    else:
        print(f"Failed to create share link for: {file_path}")
        return None