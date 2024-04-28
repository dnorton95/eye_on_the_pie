from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, session
from flask_app.models.user import User
from pprint import pprint

class Groupel:
    DB = "trips_schema"

    def __init__(self, data):
        self.id = data["id"]
        self.user_id = data["user_id"]
        self.trip_id = data["trip_id"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.groupel_id = data["id"] 
        self.user = {
            "id": data["user_id"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
        }



    @classmethod
    def user_is_joined_to_trip(cls, user_id, trip_id):
        query = "SELECT * FROM groupels WHERE user_id = %(user_id)s AND trip_id = %(trip_id)s"
        data = {"user_id": user_id, "trip_id": trip_id}
        result = connectToMySQL(cls.DB).query_db(query, data)
        return bool(result)  # If there's any result, the user is already joined to the trip

    @classmethod
    def create_groupel(cls, user_id, trip_id):
        query = "INSERT INTO groupels (user_id, trip_id) VALUES (%(user_id)s, %(trip_id)s)"
        data = {"user_id": user_id, "trip_id": trip_id}
        connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def all_groupels(cls, trip_id):
        data = {"trip_id": trip_id}
        query = """SELECT *
                FROM groupels
                JOIN users ON groupels.user_id = users.id
                WHERE groupels.trip_id = %(trip_id)s
                ORDER BY groupels.created_at DESC; """
        list_of_dicts = connectToMySQL(Groupel.DB).query_db(query, data)
        pprint(list_of_dicts)

        groupels = []
        for each_dict in list_of_dicts:
            groupel = Groupel(each_dict)
            groupels.append(groupel)
        return groupels

    @classmethod
    def create(cls):
        query = """INSERT INTO groupels (user_id, trip_id) 
                VALUES (%(user_id)s, %(trip_id)s);"""
        connectToMySQL("trips_schema").query_db(query)
        return


    @classmethod
    def delete_groupel(cls, trip_id, user_id):
        query = "DELETE FROM groupels WHERE trip_id = %s AND user_id = %s"
        data = (trip_id, user_id)
        connectToMySQL(cls.DB).query_db(query, data)
        return


    @classmethod
    def get_user_groupel_id(cls, trip_id, user_id):
        query = "SELECT id FROM groupels WHERE trip_id = %s AND user_id = %s"
        result = connectToMySQL(cls.DB).query_db(query, (trip_id, user_id))
        if result:
            return result[0]['id']
        return None
    
    @classmethod
    def has_joined_groupel(cls, trip_id, user_id):
        query = "SELECT COUNT(*) FROM groupels WHERE trip_id = %s AND user_id = %s"
        result = connectToMySQL(cls.DB).query_db(query, (trip_id, user_id))
        return result[0]['COUNT(*)'] > 0