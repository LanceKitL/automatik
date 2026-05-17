from flask import session, jsonify, request
from utils.log import audit_log
from datetime import datetime
from conn import run_query

# --- SERVICE BOOKINGS & SLOTS ---

def listServiceSlotsHandler():
    slots = run_query("""
                      SELECT * FROM service_slots 
                      WHERE is_available = %s
                      """, 
                      (1,), 
                      fetch="all")
    
    return jsonify({"data": slots}), 200

def createBookingHandler():
    data = request.get_json()
    user_id = session["user"]
    slot_id = data.get("slot_id")
    vehicle_id = data.get("vehicle_id")
    warranty_claim_id = data.get("warranty_claim_id")
    
    if not slot_id or not vehicle_id:
        return jsonify({"message": "slot and vehicle information is required."}), 400

    slot = run_query("""
                     SELECT capacity, is_available FROM service_slots 
                     WHERE slot_id = %s AND is_available = %s
                     """, 
                     (slot_id, 1), 
                     fetch="one")
    
    if not slot:
        return jsonify({"message": "Slot is unavailable."}), 400

    count_res = run_query("""
                          SELECT COUNT(*) as total FROM service_bookings 
                          WHERE slot_id = %s AND status != %s
                          """, 
                          (slot_id, 'cancelled'), 
                          fetch="one")
    
    current_bookings = count_res["total"]

    if current_bookings >= slot["capacity"]:
        return jsonify({"message": "Booking failed. Slot has reached its capacity."}), 400

    res = run_query("""
                    INSERT INTO service_bookings 
                    (customer_id, slot_id, vehicle_id, status, warranty_claim_id) 
                    VALUES (%s, %s, %s, %s, %s)
                    """, 
                    (user_id, slot_id, vehicle_id, 'pending', warranty_claim_id))

    if (current_bookings + 1) >= slot["capacity"]:
        run_query("""
                  UPDATE service_slots SET is_available = %s 
                  WHERE slot_id = %s
                  """, 
                  (0, slot_id))

    audit_log(session["user"], "Created Service Booking", "service_bookings")
    
    return jsonify({"message": "Booking created successfully!", "booking_id": res}), 201

# --- WARRANTY CLAIMS ---

def submitWarrantyClaimHandler():
    data = request.get_json()
    user_id = session["user"]
    vehicle_id = data.get("vehicle_id")
    description = data.get("description")

    if not vehicle_id or not description:
        return jsonify({"message": "vehicle and description are required."}), 400

    claim_id = run_query("""
                         INSERT INTO warranty_claims 
                         (customer_id, vehicle_id, description, status) 
                         VALUES (%s, %s, %s, %s)
                         """, 
                         (user_id, vehicle_id, description, 'submitted'))

    audit_log(session["user"], "Submitted Warranty Claim", "warranty_claims")
    
    return jsonify({"message": "Submitted successfully!", "claim_id": claim_id}), 201

def updateWarrantyStatusHandler(claim_id):
    data = request.get_json()
    new_status = data.get("status")
    resolution = data.get("resolution_text")
    
    if not new_status:
        return jsonify({"message": "status is required."}), 400

    # Reject logic: add resolution text (Requirement from PDF)
    if new_status == 'rejected' and not resolution:
        return jsonify({"message": "Resolution note is required when rejecting a claim."}), 400

    run_query("""
              UPDATE warranty_claims 
              SET status = %s, resolution_text = %s 
              WHERE claim_id = %s
              """, 
              (new_status, resolution, claim_id))

    audit_log(session["user"], f"Updated Warranty Status to {new_status}", "warranty_claims")
    
    return jsonify({"message": f"Claim status updated to {new_status}."}), 200