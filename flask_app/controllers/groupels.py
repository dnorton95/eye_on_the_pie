from flask_app import app
from flask_app.models.groupel import Groupel
from flask_app.models.user import User
from flask import flash, render_template, redirect, request, session, url_for

def get_current_user():
    """Get the currently logged-in user"""
    if 'user_id' in session:
        user_id = session['user_id']
        return User.find_user_by_id(user_id)  # Assuming you have a method to find a user by ID
    return None

@app.route('/groupels/<int:trip_id>/join', methods=['POST'])
def join_trip(trip_id):
    # Check if the user is logged in (you might need to implement this logic)
    # For example, you might have a function to get the currently logged-in user
    
    # Assuming you have a function to get the currently logged-in user
    current_user = get_current_user()

    if current_user is None:
        flash("You must be logged in to join a trip.", "error")
        return redirect(url_for('login'))  # Redirect to the login page

    # Check if the user is already joined to the trip
    if Groupel.user_is_joined_to_trip(current_user.id, trip_id):
        flash("You have already joined this trip.", "error")
        return redirect(url_for('trip_details', trip_id=trip_id))

    # Add the user to the trip's groupel table
    Groupel.create_groupel(current_user.id, trip_id)

    flash("You have successfully joined the trip!", "success")
    return redirect(url_for('trip_details', trip_id=trip_id))


@app.post("/groupels/create")
def create_groupel():
    print("Before retrieving trip_id from form")
    trip_id = request.form.get("trip_id")  # Use get method to avoid KeyError
    print("Trip ID from form:", trip_id)  # Add this line for debugging
    
    try:
        Groupel.create()
    except Exception as e:
        # Print out the exception to debug the issue
        print("Error occurred:", e)
        flash('Error occurred while creating the groupel. Please try again later.', 'error')
    
    # Redirect to a relevant page after handling the form submission
    return redirect(f"/trips/{trip_id}")


@app.post("/groupels/<int:groupel_id>/delete")
def unjoin_trip(groupel_id):
    if "user_id" not in session:
        flash("Please log in.", "login")
        return redirect("/")
    
    trip_id = request.form.get("trip_id")
    user_id = session.get("user_id")
    if user_id:
        Groupel.delete_groupel(trip_id, user_id)
        flash("You have successfully unjoined the trip.", "success")
    return redirect("/trips")
