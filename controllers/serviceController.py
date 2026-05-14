from flask import session, jsonify, request
from utils.log import audit_log
from conn import run_query


def listServiceSlotsHandler():
    slots = run_query("SELECT * FROM service_slots WHERE is_available = 1", fetch="all")
    return jsonify({"data": slots}), 200

def createServiceSlotHandler():
    data = request.get_json()
    query = "INSERT INTO service_slots (slot_date, slot_time, is_available) VALUES (%s, %s, %s)"
    params = (data['slot_date'], data['slot_time'], 1)
    res = run_query(query, params)
    
    audit_log(session["user"], "Created new service slot", "service_slots")
    return jsonify({"message": "Service slot created successfully!", "id": res}), 201

def listMyBookingsHandler():
    user_id = session["user"]
    bookings = run_query("SELECT * FROM service_bookings WHERE user_id = %s", (user_id,), fetch="all")
    return jsonify({"data": bookings}), 200

def createBookingHandler():
    data = request.get_json()
    user_id = session["user"]
    
    # Insert sa service_bookings table
    query = """
        INSERT INTO service_bookings (user_id, slot_id, booking_type, status) 
        VALUES (%s, %s, %s, %s)
    """
    params = (user_id, data['slot_id'], data['type'], 'pending')
    booking_id = run_query(query, params)
    
    run_query("UPDATE service_slots SET is_available = 0 WHERE slot_id = %s", (data['slot_id'],))
    
    audit_log(user_id, f"Booked service/test drive (ID: {booking_id})", "service_bookings")
    return jsonify({"message": "Booking successful!", "booking_id": booking_id}), 201

def updateBookingStatusHandler(booking_id):
    data = request.get_json()
    status = data.get("status") # e.g., 'confirmed', 'completed', 'cancelled'
    
    run_query("UPDATE service_bookings SET status = %s WHERE booking_id = %s", (status, booking_id))
    
    audit_log(session["user"], f"Updated booking {booking_id} status to {status}", "service_bookings")
    return jsonify({"message": "Booking status updated!"}), 200

def listWarrantyClaimsHandler():
    # Admin view para makita lahat, o user view para sa sariling claims
    if session["role"] == "admin":
        claims = run_query("SELECT * FROM warranty_claims", fetch="all")
    else:
        claims = run_query("SELECT * FROM warranty_claims WHERE user_id = %s", (session["user"],), fetch="all")
    return jsonify({"data": claims}), 200

def submitWarrantyClaimHandler():
    data = request.get_json()
    user_id = session["user"]
    
    query = """
        INSERT INTO warranty_claims (user_id, vehicle_id, description, status) 
        VALUES (%s, %s, %s, 'pending')
    """
    params = (user_id, data['vehicle_id'], data['description'])
    claim_id = run_query(query, params)
    
    audit_log(user_id, "Submitted warranty claim", "warranty_claims")
    return jsonify({"message": "Warranty claim submitted successfully!", "claim_id": claim_id}), 201