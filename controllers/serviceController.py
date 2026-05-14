from flask import Flask, request, jsonify, session
from conn import run_query

# Services_slots
def getServicesSlot():
    service_slots = None
    if "service_slots" in session:
        return jsonify({"data": service_slots}), 200
    
    service_slots = run_query("SELECT * FROM service_slots", fetch="all")
    
    return jsonify ({"data": service_slots}), 200

def createServiceSlots():
    data = request.get_json()
    slot_id = data.get("slot_id")
    slot_datetime = data.get("slot_datetime")
    slot_type = data.get("slot_type")
    capacity = data.get("capacity")
    is_available = data.get("is_available")
    
    
    service_slot = run_query("""
                             INSERT INTO service_slots
                             (slot_datetime, slot_type, capacity, 
                             is_available, created_at)
                             VALUES (%s,%s,%s,%s,%s)""",
                             ( slot_datetime, slot_type ,capacity,
                                 is_available) 
                             )
    if not service_slot:
        return jsonify({"message":" The Slot was not been added. Execution Failed"}), 400\
            
    return jsonify({"message": " New Slot wass successfully added"}), 200   


#Service_Booking
def getServiceBooking(id):
    service_booking = None
    if "service_bookings" in session:
        return jsonify({"data": service_booking}), 200
    
    service_booking = run_query("SELECT * FROM service_booking WHERE booking_id = %s",
                                (id, ), fetch="all")
    
    return jsonify ({"data": service_booking}), 200


def creatServiceBooking():
    data = request.get_json()
    
    customer_id = data.get("customer_id")
    vehicle_id = data.get("vehicle_id")
    slot_id = data.get("slot_id")
    booking_type = data.get("booking_type")
    warranty_claim_id = data.get("warranty_claim_id")
    notes = data.get("notes")
    status = data.get("status")
    
    service_booking = run_query("""
                                INSERT INTO service_bookings
                                ( customer_id, vehicle_id,
                                slot_id, booking_type, warranty_claim_id,
                                notes, status) 
                                VALUES 
                                (%s,%s,%s,%s,%s,%s,%s,%s) 
                                """,
                                (customer_id,vehicle_id,
                                 slot_id, booking_type, warranty_claim_id,
                                 notes, status))
    
    if not service_booking:
        return jsonify({"messege": "Your booking has not been added. Execution Failed"}), 400
    
    return jsonify({"messege": "Your booking was succesfuly Added"})

def updServiceBooking(id):
    data = request.get_json()
    
    customer_id = data.get("customer_id")
    vehicle_id = data.get("vehicle_id")
    slot_id = data.get("slot_id")
    booking_type = data.get("booking_type")
    warranty_claim_id = data.get("warranty_claim_id")
    notes = data.get("notes")
    status = data.get("status")
    
    service_booking = run_query("""
                                UPDATES service_bookings
                                SET customer_id = %s, vehicle_id = %s,
                                slot_id = %s, booking_type = %s, warranty_claim_id = %s,
                                notes = %s, status = %s WHERE bookin_id = %s
                                """, (customer_id,vehicle_id,slot_id,
                                      booking_type, warranty_claim_id,
                                      notes, status, id))
    
    if not service_booking:
        return jsonify({"messege": "Updates unsuccessful. Execution Failed"}), 400
    
    return jsonify({"messege": "Updated Successfully"}), 200


def getWarrantyClaims():
    warranty_claims = None
    if "warranty_claims" in session:
        return jsonify({"data": warranty_claims}), 200
    
    warranty_claims = run_query("SELECT * FROM warranty_claims", fetch="all")
    

    return jsonify({"data":warranty_claims}), 200


def submitWarrantyClaims():
    data = request.get_json()
    
    sale_id = data.get("sale_id")
    vehicle_id = data.get("vehicle_id")
    claim_type = data.get("claim_type")
    description = data.get("description")
    status = data.get("status")
    
    warranty_claims = run_query("""
                                INSERT INTO warranty_claims
                                (sale_id, vehicle_id, claim_type, description,
                                status) VALUES (%s, %s,%s,%s,%s)""",
                                (sale_id,vehicle_id,claim_type,
                                 description, status))
    
    if not warranty_claims:
        return jsonify({"messege": "Submision unsuccessful. Execution failed"}), 400
    
    return jsonify({"messege": "Submited successfuly"}), 200



def updWarrantyClaims(id):
    data = request.get_json()
    
    claim_type = data.get("claim_type")
    status = data.get("status")
    reviewed_by = data.get("reviewed_by")
    resolution = data.get("resolution")
    resolved_at = data.get("resolved_at")
    
    warranty_claims = run_query("""
                                UPDATE warranty_claims
                                SET claim_type =%s, status = %s, reveiwed_by = %s,
                                resolution =%s, resolved_at = %s WHERE claim_id =%s
                                """, (claim_type,status, reviewed_by, resolution,
                                      resolved_at, id)
    )
    
    if not warranty_claims:
        return jsonify({"message": "Updates Unsuccessful. Execution Failed"}), 400
    
    
    
    return jsonify({"message": "Updated successfuly"}), 200