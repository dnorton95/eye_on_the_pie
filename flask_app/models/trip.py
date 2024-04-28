from flask import flash
from datetime import datetime
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User
from flask_app.models.groupel import Groupel




class Trip:
    DB = "trips_schema"
    def __init__(self, data):
        self.id = data["id"]
        self.location = data["location"]
        self.booking_link = data["booking_link"]
        self.booking_title = data["booking_title"]
        self.address = data["address"]
        self.check_in = data["check_in"]
        self.check_out = data["check_out"]
        self.notes = data["notes"]
        self.itinerary = data["itinerary"]
        self.total_cost = data["total_cost"]
        self.photo_path = data["photo_path"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.user_id = data["user_id"]
        self.user = None
        planner = {"id": data["user_id"]}
        if "first_name" in data:
            planner["first_name"] = data["first_name"]
        if "last_name" in data:
            planner["last_name"] = data["last_name"]
        self.planner = planner
        self.groupels = Groupel.all_groupels(self.id)

# VALIDATOR
    @staticmethod
    def form_is_valid(trip_input_data):
        is_valid = True
        # TEXT VALIDATOR
        if len(trip_input_data["location"]) == 0:
            flash("Please enter location.")
            is_valid = False
        elif len(trip_input_data["location"]) < 3:
            flash("Location must be at least three characters.")
            is_valid = False

        if len(trip_input_data["booking_link"]) == 0:
            flash("Please enter booking_link.")
            is_valid = False
        elif len(trip_input_data["booking_link"]) < 3:
            flash("Booking_link field must be at least three characters.")
            is_valid = False

        if len(trip_input_data["booking_title"]) == 0:
            flash("Please enter booking_title.")
            is_valid = False
        elif len(trip_input_data["booking_title"]) < 3:
            flash("Booking name field must be at least three characters.")
            is_valid = False

        if len(trip_input_data["address"]) == 0:
            flash("Please enter address.")
            is_valid = False
        elif len(trip_input_data["address"]) < 3:
            flash("Address field must be at least three characters.")
            is_valid = False

        if len(trip_input_data["notes"]) == 0:
            flash("Please enter notes.")
            is_valid = False
        elif len(trip_input_data["notes"]) < 3:
            flash("Notes field must be at least three characters.")
            is_valid = False

        if len(trip_input_data["itinerary"]) == 0:
            flash("Please enter itinerary.")
            is_valid = False
        elif len(trip_input_data["itinerary"]) < 3:
            flash("Itinerary field must be at least three characters.")
            is_valid = False
        # TEXT VALIDATOR


        # DIGIT VALIDATOR
        if len(trip_input_data["total_cost"]) == 0:
            flash("Please enter total cost.")
            is_valid = False
        elif not trip_input_data["total_cost"].isdigit():
            flash("Total cost must be an integer.")
            is_valid = False
        # DIGIT VALIDATOR


        # DATE VALIDATOR
        def validate_check_in(check_in_date):
            try:
                # Attempt to parse the input as a date with the expected format
                datetime.strptime(check_in_date, "%Y-%m-%d")
                return True, None  # Return True if successful
            except ValueError:
                # If parsing fails, it's not in the correct format
                return False, "Check-in date must be in the format YYYY-MM-DD."

        if len(trip_input_data["check_in"]) == 0:
            flash("Please enter check-in date.")
            is_valid = False
        elif not validate_check_in(trip_input_data["check_in"]):
            flash("Check-in date must be in the format YYYY-MM-DD.")
            is_valid = False

        if len(trip_input_data["check_in"]) == 0:
            flash("Please enter check-in date.")
            is_valid = False
        elif not validate_check_in(trip_input_data["check_in"]):
            flash("Check-in date must be in the format YYYY-MM-DD.")
            is_valid = False
        # DATE VALIDATOR

        return is_valid
    
    # IMAGE VALIDATOR:
    @staticmethod
    def validate_photo(file):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if not file:
            return False, "Please upload a photo."
        if not allowed_file(file.filename):
            return False, "Invalid file type. Please upload a photo."
        return True, None
    # IMAGE VALIDATOR

# VALIDATOR

    @classmethod
    def find_upcoming_joined_trips_by_user_id(cls, user_id):
        current_date = datetime.now().strftime('%Y-%m-%d')
        query = """
            SELECT t.*
            FROM trips t
            JOIN groupels g ON t.id = g.trip_id
            WHERE g.user_id = %(user_id)s
            AND t.check_in >= %(current_date)s
        """
        data = {"user_id": user_id, "current_date": current_date}
        list_of_dicts = connectToMySQL(cls.DB).query_db(query, data)

        trips = []
        for each_dict in list_of_dicts:
            trip = Trip(each_dict)
            trips.append(trip)
        return trips

    @classmethod
    def find_previous_joined_trips_by_user_id(cls, user_id):
        current_date = datetime.now().strftime('%Y-%m-%d')
        query = """
            SELECT t.*
            FROM trips t
            JOIN groupels g ON t.id = g.trip_id
            WHERE g.user_id = %(user_id)s
            AND t.check_out < %(current_date)s
        """
        data = {"user_id": user_id, "current_date": current_date}
        list_of_dicts = connectToMySQL(cls.DB).query_db(query, data)

        trips = []
        for each_dict in list_of_dicts:
            trip = Trip(each_dict)
            trips.append(trip)
        return trips


    @classmethod
    def find_all_trips(cls):
        query = """SELECT * FROM trips JOIN users ON trips.user_id = users.id"""
        list_of_dicts = connectToMySQL(Trip.DB).query_db(query)

        trips = []
        for each_dict in list_of_dicts:
            trip = Trip(each_dict)
            trips.append(trip)
        return trips
    
    @classmethod
    def get_all_trips(cls):
        query = """
            SELECT trips.*, users.id as user_id, users.first_name, users.last_name
            FROM trips
            JOIN users ON trips.user_id = users.id
        """
        results = connectToMySQL(cls.DB).query_db(query)
        
        all_trips = []
        for result in results:
            trip_data = {
                "id": result["id"],
                "location": result["location"],
                "booking_link": result["booking_link"],
                "booking_title": result["booking_title"],
                "address": result["address"],
                "check_in": result["check_in"],
                "check_out": result["check_out"],
                "notes": result["notes"],
                "itinerary": result["itinerary"],
                "total_cost": result["total_cost"],
                "photo_path": result["photo_path"],
                "created_at": result["created_at"],
                "updated_at": result["updated_at"],
                "user_id": {
                }
            }
            trip = Trip(trip_data)
            all_trips.append(trip)
        
        return all_trips

    
    @classmethod
    def find_all_trips_with_users(cls):
        query = """SELECT * FROM trips JOIN users ON trips.user_id = users.id"""

        list_of_dicts = connectToMySQL(Trip.DB).query_db(query)

        trips = []
        for each_dict in list_of_dicts:
            trip = Trip(each_dict)
            user_input_data = {
                "id": each_dict["id"],
                "first_name": each_dict["first_name"],
                "last_name": each_dict["last_name"],
                "email": each_dict["email"],
                "password": each_dict["password"],
                "created_at": each_dict["created_at"],
                "updated_at": each_dict["updated_at"],
            }
            user = User(user_input_data)
            trip.user = user
            trips.append(trip)
        return trips
    
    @classmethod
    def find_trip_by_id_with_user(cls, trips_id):
        """This method find a trip by the id and user by the record id"""
        query = """
            SELECT trips.*, users.*
            FROM trips
            JOIN users ON trips.user_id = users.id 
            WHERE trips.id = %(trips_id)s
        """

        data = {"trips_id": trips_id}
        list_of_dicts = connectToMySQL(Trip.DB).query_db(query, data)

        if len(list_of_dicts) == 0:
            return None
        
        trip = Trip(list_of_dicts[0])
        user_input_data = {
            "id": list_of_dicts[0]["users.id"],
            "first_name": list_of_dicts[0]["first_name"],
            "last_name": list_of_dicts[0]["last_name"],
            "email": list_of_dicts[0]["email"],
            "password": list_of_dicts[0]["password"],
            "created_at": list_of_dicts[0]["users.created_at"],
            "updated_at": list_of_dicts[0]["users.updated_at"],
        }
        trip.user = User(user_input_data)
        return trip


    
    @classmethod
    def new_trip(cls, trip_input_data):
        try:
            # Insert trip data into the trips table
            query_trip = """
            INSERT INTO trips
            (location, booking_link, booking_title, address, check_in, check_out,
            notes, itinerary, total_cost, photo user_id)
            VALUES
            (%(location)s, %(booking_link)s, %(booking_title)s, %(address)s, 
            %(check_in)s, %(check_out)s, %(notes)s,
            %(itinerary)s, %(total_cost)s, %(photo)s, %(user_id)s)
            """
            trips_id = connectToMySQL(cls.DB).query_db(query_trip, trip_input_data)

            return trips_id
        except Exception as e:
            # Handle the error
            print(f"An error occurred: {str(e)}")
            return None
        
    @classmethod
    def create(cls, form_data):
        query = """
        INSERT INTO trips
        (location, booking_link, booking_title, address, check_in, check_out,
        notes, itinerary, total_cost, photo_path, user_id)
        VALUES
        (%(location)s, %(booking_link)s, %(booking_title)s, %(address)s, 
        %(check_in)s, %(check_out)s, %(notes)s,
        %(itinerary)s, %(total_cost)s, %(photo_path)s, %(user_id)s)
        """
        trip_id = connectToMySQL(Trip.DB).query_db(query, form_data)
        return trip_id


    
    @classmethod
    def update(cls, trips_id, trip_input_data):
        query = """UPDATE trips 
        SET location = %(location)s, 
        booking_link = %(booking_link)s,
        booking_title = %(booking_title)s, 
        address = %(address)s ,
        check_in = %(check_in)s ,
        check_out = %(check_out)s ,
        notes = %(notes)s ,
        itinerary = %(itinerary)s ,
        total_cost = %(total_cost)s ,
        photo_path = %(photo_path)s 
        WHERE id = %(trips_id)s;"""
        data = {
            "trips_id": trips_id,
            "location": trip_input_data["location"],
            "booking_link": trip_input_data["booking_link"],
            "booking_title": trip_input_data["booking_title"],
            "address": trip_input_data["address"],
            "check_in": trip_input_data["check_in"],
            "check_out": trip_input_data["check_out"],
            "notes": trip_input_data["notes"],
            "itinerary": trip_input_data["itinerary"],
            "total_cost": trip_input_data["total_cost"],
            "photo_path": trip_input_data["photo_path"],

        }
        connectToMySQL(Trip.DB).query_db(query, data)
    
    @classmethod
    def delete_by_id(cls, trip_id):
        connectToMySQL(cls.DB).query_db("DELETE FROM groupels WHERE trip_id = %s", (trip_id,))
        connectToMySQL(cls.DB).query_db("DELETE FROM trips WHERE id = %s", (trip_id,))
    
    @classmethod
    def count_by_location(cls, location):
        query = """SELECT COUNT(location) AS "count"
        FROM trips WHERE location = %(location)s"""
        data = {"location": location}
        list_of_dicts = connectToMySQL(Trip.DB).query_db(query, data)
        print(list_of_dicts)
        return list_of_dicts[0]["count"]
    
    @classmethod
    def find_trip_by_id(cls, trip_id):
        query = "SELECT * FROM trips WHERE id = %s"
        result = connectToMySQL(cls.DB).query_db(query, (trip_id,))
        return cls(result[0]) if result else None

    
    @classmethod
    def find_trips_by_user_id(cls, user_id):
        """Find trips associated with a specific user"""
        query = """
            SELECT trips.*, users.*
            FROM trips
            JOIN users ON trips.user_id = users.id 
            WHERE users.id = %(user_id)s
        """

        data = {"user_id": user_id}
        list_of_dicts = connectToMySQL(Trip.DB).query_db(query, data)

        trips = []
        for trip_data in list_of_dicts:
            trip = Trip(trip_data)

            user_input_data = {
                "id": trip_data["users.id"],
                "first_name": trip_data["first_name"],
                "last_name": trip_data["last_name"],
                "email": trip_data["email"],
                "password": trip_data["password"],
                "created_at": trip_data["users.created_at"],
                "updated_at": trip_data["users.updated_at"],
            }
            trip.user = User(user_input_data)
            trips.append(trip)

        return trips
    
    @classmethod
    def find_all_trips_with_users_and_groupels(cls):
        query = """
            SELECT 
                trips.*, 
                users.id AS user_id, 
                users.first_name, 
                users.last_name,
                groupels.id AS groupel_id, 
                groupels.trip_id
            FROM 
                trips
            JOIN 
                users ON trips.user_id = users.id
            LEFT JOIN 
                groupels ON trips.id = groupels.trip_id
            ORDER BY 
                trips.id, 
                groupels.created_at DESC
        """
        results = connectToMySQL(cls.DB).query_db(query)

        trips = []
        current_trip = None
        for result in results:
            if not current_trip or current_trip.id != result["id"]:
                current_trip = cls(result)
                current_trip.groupels = []  # Initialize groupels list for the current trip
                trips.append(current_trip)

            if result["groupel_id"]:  # If there is a groupel associated with the trip
                current_trip.groupels.append(Groupel(result))  # Add the groupel to the current trip's groupels list

        return trips


    @classmethod
    def find_upcoming_trips_by_user_id(cls, user_id):
        # Query the database to find upcoming trips for the given user ID
        current_date = datetime.now().strftime('%Y-%m-%d')
        query = """
            SELECT * 
            FROM trips 
            WHERE user_id = %(user_id)s 
            AND check_in >= %(current_date)s
        """
        data = {"user_id": user_id, "current_date": current_date}
        list_of_dicts = connectToMySQL(cls.DB).query_db(query, data)

        trips = []
        for each_dict in list_of_dicts:
            trip = Trip(each_dict)
            trips.append(trip)
        return trips

    @classmethod
    def find_previous_trips_by_user_id(cls, user_id):
        # Query the database to find previous trips for the given user ID
        current_date = datetime.now().strftime('%Y-%m-%d')
        query = """
            SELECT * 
            FROM trips 
            WHERE user_id = %(user_id)s 
            AND check_out < %(current_date)s
        """
        data = {"user_id": user_id, "current_date": current_date}
        list_of_dicts = connectToMySQL(cls.DB).query_db(query, data)

        trips = []
        for each_dict in list_of_dicts:
            trip = Trip(each_dict)
            trips.append(trip)
        return trips

    @classmethod
    def find_trip_by_location(cls, location):
        query = "SELECT * FROM trips WHERE location = %s"
        result = connectToMySQL(cls.DB).query_db(query, (location,))
        if result:
            return cls(result[0])  # Assuming only one trip is found for a given location
        return None
    
    @classmethod
    def find_trip_with_groupelers(cls, trip_id):
        # Modify your database query to fetch trip data along with associated groupelers
        query = """
            SELECT t.*, g.id AS groupeler_id, g.user_id AS groupeler_user_id
            FROM trips t
            LEFT JOIN groupels g ON t.id = g.trip_id
            WHERE t.id = %s
        """
        data = (trip_id,)
        result = connectToMySQL(cls.DB).query_db(query, data)

        if result:
            trip_data = result[0]  # Assuming only one row is returned for the trip
            trip = cls(trip_data)
            
            # Assign groupelers data to the trip object
            for row in result:
                groupeler_data = {
                    "id": row["groupeler_id"],
                    "user_id": row["groupeler_user_id"],
                    # Other groupeler attributes...
                }
                trip.groupels.append(Groupel(groupeler_data))  # Assuming you have a Groupeler class
                
            return trip
        else:
            return None
        