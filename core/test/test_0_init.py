import logging
from pymongo import MongoClient
from settings import SETTINGS
from settings import ENV

LOGGER = logging.getLogger(__name__)
client = MongoClient(SETTINGS.MONGO_URI)
db = client.get_database(SETTINGS.DATABASE_NAME)



def test_0_setup_and_teardown():
    clear_all_collections()


# Define a function to clear all collections in the database
def clear_all_collections():
    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        db.drop_collection(collection_name)


def test_1_db_config():
    assert ENV == "testing"