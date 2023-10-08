from constants import *
from imports import *


def get_uuid(text):
    return uuid.uuid3(uuid.NAMESPACE_DNS, text)
