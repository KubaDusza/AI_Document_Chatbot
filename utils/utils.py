from constants import *
from imports import *


def get_uuid(text):
    return uuid.uuid3(uuid.NAMESPACE_DNS, text)




def get_base64_of_bin_file(binary):
    return base64.b64encode(binary).decode()