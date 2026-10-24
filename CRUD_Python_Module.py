"""
CRUD_Python_Module.py
 
Reusable CRUD (Create, Read, Update, Delete) module for the Grazioso Salvare
project. Provides an AnimalShelter class that connects to the Austin Animal
Center (aac) database in MongoDB using an authenticated user account.
 
Author: Carrie Cummings
"""
 
from pymongo import MongoClient
from pymongo.errors import PyMongoError
 
 
class AnimalShelter(object):
    """CRUD operations for the animals collection in MongoDB."""
 
    def __init__(self, username, password, host='localhost', port=27017,
                 db_name='aac', collection_name='animals'):
        """
        Initialize the connection to MongoDB.
 
        username        -- MongoDB user (e.g., 'aacuser')
        password        -- password for that user
        host, port      -- where MongoDB is running (defaults for Codio)
        db_name         -- database to use (default 'aac')
        collection_name -- collection to use (default 'animals')
        """
        try:
            # Build the connection string with the credentials passed in,
            # so no password is hard-coded in this file
            self.client = MongoClient(
                'mongodb://%s:%s@%s:%d/?authSource=admin'
                % (username, password, host, port)
            )
            self.database = self.client[db_name]
            self.collection = self.database[collection_name]
        except PyMongoError as error:
            print(f"Could not connect to MongoDB: {error}")
            raise
 
    def create(self, data):
        """
        Insert a single document into the collection.
 
        data -- dict containing the document to insert
        Returns True if the insert succeeded, otherwise False.
        """
        # Verify that data is a non-empty dictionary before attempting insert
        if not data or not isinstance(data, dict):
            print("Nothing to save, because data parameter is empty or invalid")
            return False
 
        try:
            # Insert the document and report whether MongoDB acknowledged it
            result = self.collection.insert_one(data)
            return result.acknowledged
        except PyMongoError as error:
            print(f"An error occurred during insert: {error}")
            return False
 
    def read(self, query):
        """
        Find documents matching the query.
 
        query -- dict of key/value pairs, e.g. {"animal_type": "Dog"}
        Returns a list of matching documents, or an empty list.
        """
        # Verify that query is a dictionary before attempting find
        if query is None or not isinstance(query, dict):
            print("Query parameter is empty or invalid")
            return []
 
        try:
            # find() returns a cursor; list() pulls every matching document
            cursor = self.collection.find(query)
            return list(cursor)
        except PyMongoError as error:
            print(f"An error occurred during read: {error}")
            return []
 
    def update(self, query, new_values, update_all=True):
        """
        Update document(s) matching the query.
 
        query      -- dict of key/value pairs to find the document(s)
        new_values -- dict of changes, e.g. {"$set": {"breed": "Beagle"}}
                      (a plain dict like {"breed": "Beagle"} also works)
        update_all -- True uses update_many(), False uses update_one()
        Returns the number of documents modified (0 if none or on error).
        """
        # Both a query and new values are required
        if not query or not new_values:
            print("Update requires both a query and new values")
            return 0
 
        # Wrap plain dicts in $set so callers don't have to remember it
        if not any(key.startswith('$') for key in new_values):
            new_values = {'$set': new_values}
 
        try:
            if update_all:
                result = self.collection.update_many(query, new_values)
            else:
                result = self.collection.update_one(query, new_values)
            return result.modified_count
        except PyMongoError as error:
            print(f"An error occurred during update: {error}")
            return 0
 
    def delete(self, query, delete_all=True):
        """
        Delete document(s) matching the query.
 
        query      -- dict of key/value pairs to find the document(s)
        delete_all -- True uses delete_many(), False uses delete_one()
        Returns the number of documents removed (0 if none or on error).
        """
        # Safety guard: an empty query {} would delete the entire collection
        if not query:
            print("Delete requires a non-empty query")
            return 0
 
        try:
            if delete_all:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
            return result.deleted_count
        except PyMongoError as error:
            print(f"An error occurred during delete: {error}")
            return 0