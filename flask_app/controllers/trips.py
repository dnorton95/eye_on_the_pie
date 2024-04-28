from flask_app import app
from flask_app.models.trip import Trip
from flask_app.models.user import User
from flask_app.models.groupel import Groupel
from flask import flash, render_template, redirect, request, session
import os

@app.route("/dashboard")
def trips():
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")

    user_id = session["user_id"]
    user = User.find_user_by_id(user_id)
    user_trips = Trip.find_trips_by_user_id(user_id)
    upcoming_trips = Trip.find_upcoming_trips_by_user_id(user_id)
    previous_trips = Trip.find_previous_trips_by_user_id(user_id)
    joined_upcoming_trips = Trip.find_upcoming_joined_trips_by_user_id(user_id)
    joined_previous_trips = Trip.find_previous_joined_trips_by_user_id(user_id)

    return render_template(
        "dashboard.html",
        user=user,
        user_trips=user_trips,
        upcoming_trips=upcoming_trips,
        previous_trips=previous_trips,
        joined_upcoming_trips=joined_upcoming_trips,
        joined_previous_trips=joined_previous_trips
    )

@app.get("/trips")
def get_all_trips():
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")
    
    trips = Trip.find_all_trips_with_users_and_groupels()
    user = User.find_user_by_id(session["user_id"])

    groupels = {}
    for trip in trips:
        groupels[trip.id] = Groupel.all_groupels(trip.id)

    print(groupels)
    has_joined_groupel = Groupel.has_joined_groupel

    return render_template("all_trips.html", trips=trips, user=user, groupels=groupels, has_joined_groupel=has_joined_groupel)


@app.post("/trips/create")
def create_trip():
    # Check Session for User
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")

    user_id = session["user_id"]
    # Check Session for User

    print("Form data:", request.form)

    # Run trip class validator
    if not Trip.form_is_valid(request.form):
        return redirect("/dashboard")
    # Run trip class validator

    # Validate the photo
    is_valid_photo, photo_error_message = Trip.validate_photo(request.files.get('photo'))
    if not is_valid_photo:
        flash(photo_error_message)
        return redirect("/trips/create")  # Redirect to the new trip form page

    # Save the uploaded image
    image_file = request.files['photo']
    image_path = save_image(image_file)

    # Update the form data to include the image path
    form_data = request.form.copy()
    form_data['photo_path'] = image_path
    form_data['user_id']= user_id

    if "groupels" in form_data:
        session["groupels"] = form_data["groupels"]

    # Check if the trip name is unique
    if Trip.count_by_location(form_data["location"]) >= 1:
        flash("Trip already exists!")
        return redirect("/dashboard")

    if "groupels" in session:
        session.pop("groupels")

    Trip.create(form_data)

    new_trip = Trip.find_trip_by_location(form_data["location"])
    new_trip_id = new_trip.id

    flash("Trip successfully posted")
    return redirect(f"/trips/{new_trip_id}")

def save_image(image_file):
    # Ensure the upload folder exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the image to the uploads folder
    image_path = os.path.join(upload_folder, image_file.filename)
    image_file.save(image_path)
    return image_path

@app.get("/trips/new")
def render_trips():
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")
    return render_template("new_trip.html")

@app.get("/trips/<trip_id>")
def trip_details(trip_id):
    trip_id = int(trip_id)  # Convert trip_id to an integer if necessary

    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")

    groupels = Groupel.all_groupels(trip_id)
    trip = Trip.find_trip_by_id_with_user(trip_id)
    user = User.find_user_by_id(session["user_id"])
    user_id = session.get('user_id')
    has_joined_groupel = Groupel.has_joined_groupel(trip_id, user_id)

    user_groupel_id = None  # Initialize user_groupel_id

    if has_joined_groupel:
        user_groupel_id = Groupel.get_user_groupel_id(trip_id, user_id)  # Retrieve user's groupel ID

    if not trip.booking_link.startswith('http'):
        trip.booking_link = 'http://' + trip.booking_link

    return render_template('trip_details.html', trip=trip, groupels=groupels, user=user, has_joined_groupel=has_joined_groupel, user_groupel_id=user_groupel_id)


@app.get("/trips/<int:trip_id>/edit")
def edit_trip(trip_id):
    # Check if user is in session
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")

    # Pass in the trip and user variables
    trip = Trip.find_trip_by_id(trip_id)
    user = User.find_user_by_id(session["user_id"])

    # If trip is found
    if trip:
        # If there's a photo, store its path
        photo_path = trip.photo_path or ""
        # If there's an itinerary, store its content
        itinerary_content = trip.itinerary or ""
        return render_template("edit_trip.html", trip=trip, user=user, photo_path=photo_path, itinerary_content=itinerary_content)
    else:
        flash("Trip not found.", "error")
        return redirect("/")



@app.post("/trips/update")
def update_trip():
    # Check if user is in session
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")

    # Check for trip_id
    if "trip_id" not in request.form:
        flash("Trip ID is missing.", "error")
        return redirect("/")

    trip_id = request.form["trip_id"]
    trip = Trip.find_trips_by_user_id(trip_id)

    # Validate the existence of trip_id and other necessary form fields
    if not Trip.form_is_valid(request.form):
        flash("Invalid trip data.", "error")
        return redirect(f"/trips/{trip_id}/edit")
    
    # Check if a new photo is uploaded
    if "photo" in request.files:
        is_valid_photo, photo_error_message = Trip.validate_photo(request.files.get('photo'))
        if not is_valid_photo:
            flash(photo_error_message)
            return redirect(f"/trips/{trip_id}/edit")  # Redirect to the edit trip form page
        
        # Save the uploaded image
        image_file = request.files['photo']
        image_path = save_image(image_file)

        # Update the form data to include the new image path
        trip_input_data = request.form.copy()
        trip_input_data['photo_path'] = image_path
    
    else:
        # If no new photo is uploaded, keep the existing photo path
        trip_input_data = request.form.copy()
        trip_input_data['photo_path'] = trip.photo_path

    # Update the trip using Trip.update() method
    Trip.update(trip_id, trip_input_data)

    flash("Trip successfully updated")
    return redirect(f"/trips/{trip_id}")



@app.post("/trips/<int:trip_id>/delete")
def delete_trip(trip_id):
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")

    user_id = session.get("user_id")
    trip = Trip.find_trip_by_id(trip_id)
    if not trip:
        flash("Trip not found.", "warning")
        return redirect("/trips")

    if trip.user_id != user_id:
        flash("You are not authorized to delete this trip.", "warning")
        return redirect("/trips")

    Trip.delete_by_id(trip_id)
    flash("Trip deleted successfully.", "success")
    return redirect("/trips")



