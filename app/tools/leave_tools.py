import datetime
from bson import ObjectId
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from typing import Optional, List

# --- නිවැරදි කළ යුතු ප්‍රධානතම ස්ථානය ---
# dateutil.parser වෙතින් 'parse' ශ්‍රිතය import කිරීම
from dateutil.parser import parse

# Database collection එක import කිරීම
from app.utils.db import leave_requests_collection, db

# --- Input Schemas (කිසිදු වෙනසක් නැත) ---
class CreateLeaveRequestInput(BaseModel):
    employee_id: str = Field(description="The unique ID of the employee making the request.")
    supervisor_id: str = Field(description="The unique ID of the employee's supervisor.")
    leave_type: str = Field(description="Type of leave (e.g., 'Annual', 'Sick').")
    start_date: str = Field(description="Start date of leave. Should be a clear date like '2025-07-15'.")
    end_date: str = Field(description="End date of leave. Should be a clear date like '2025-07-16'.")
    reason: Optional[str] = Field(description="Reason for leave.")

class GetMyLeaveRequestsInput(BaseModel):
    employee_id: str = Field(description="The unique ID of the employee.")

class GetPendingSupervisorRequestsInput(BaseModel):
    supervisor_id: str = Field(description="The unique ID of the supervisor.")
    
class GetPendingHRRequestsInput(BaseModel):
    pass

class ApproveRejectRequestInput(BaseModel):
    request_id: str = Field(description="The unique ID of the leave request (ObjectId).")
    new_status: str = Field(description="The new status: 'approved_by_supervisor', 'approved_by_hr', or 'rejected'.")
    rejection_reason: Optional[str] = Field(description="Reason for rejection, if applicable.")
    approver_id: str = Field(description="The employee ID of the person approving/rejecting.")
    approver_role: str = Field(description="The role of the person approving/rejecting ('supervisor' or 'hr').")


# --- Tools ---

@tool("create_leave_request", args_schema=CreateLeaveRequestInput)
def create_leave_request(employee_id: str, supervisor_id: str, leave_type: str, start_date: str, end_date: str, reason: Optional[str] = None) -> str:
    """Creates a new leave request for an employee."""
    try:
        print("\n--- [DEBUG] Inside create_leave_request tool ---")
        print(f"[DEBUG] Attempting to parse dates: start='{start_date}', end='{end_date}'")
        
        # 'parse' ශ්‍රිතය දැන් නිවැරදිව ක්‍රියා කරයි
        parsed_start_date = parse(start_date)
        parsed_end_date = parse(end_date)
        print(f"[DEBUG] Dates parsed successfully.")

        request_data = {
            "employee_id": employee_id,
            "supervisor_id": supervisor_id,
            "leave_type": leave_type,
            "start_date": parsed_start_date,
            "end_date": parsed_end_date,
            "reason": reason,
            "status": "pending_supervisor_approval",
            "requested_at": datetime.datetime.now(datetime.timezone.utc)
        }
        print(f"[DEBUG] Data document prepared: {request_data}")

        print("[DEBUG] Pinging database server...")
        server_info = db.client.server_info()
        print(f"[DEBUG] Ping successful. Server version: {server_info['version']}")
        
        print("[DEBUG] Attempting to insert document into collection...")
        result = leave_requests_collection.insert_one(request_data)
        
        if result.acknowledged:
            print(f"✅ [SUCCESS] MongoDB acknowledged the insert. Document ID: {result.inserted_id}")
            return f"Successfully created the leave request. The request ID is {result.inserted_id}."
        else:
            print("❌ [FAILURE] MongoDB did NOT acknowledge the insert.")
            return "There was a problem creating the request. The database did not confirm the entry."

    except Exception as e:
        print(f"❌ [DEBUG] AN EXCEPTION OCCURRED in create_leave_request: {e}")
        import traceback
        traceback.print_exc()
        return f"An internal error occurred: {str(e)}."

# --- අනෙකුත් tools (කිසිදු වෙනසක් නැත) ---

@tool("get_my_leave_requests", args_schema=GetMyLeaveRequestsInput)
def get_my_leave_requests(employee_id: str) -> list:
    """Fetches all leave requests for a specific employee."""
    requests = list(leave_requests_collection.find({"employee_id": employee_id}))
    for req in requests:
        req['_id'] = str(req['_id'])
    return requests

@tool("get_pending_supervisor_requests", args_schema=GetPendingSupervisorRequestsInput)
def get_pending_supervisor_requests(supervisor_id: str) -> list:
    """Fetches leave requests pending approval for a specific supervisor."""
    requests = list(leave_requests_collection.find({
        "supervisor_id": supervisor_id,
        "status": "pending_supervisor_approval"
    }))
    for req in requests:
        req['_id'] = str(req['_id'])
    return requests
    
@tool("get_pending_hr_requests", args_schema=GetPendingHRRequestsInput)
def get_pending_hr_requests() -> list:
    """Fetches leave requests pending final approval from HR."""
    requests = list(leave_requests_collection.find({
        "status": "approved_by_supervisor"
    }))
    for req in requests:
        req['_id'] = str(req['_id'])
    return requests

@tool("approve_or_reject_request", args_schema=ApproveRejectRequestInput)
def approve_or_reject_request(request_id: str, new_status: str, approver_id: str, approver_role: str, rejection_reason: Optional[str] = None) -> str:
    """Approves or rejects a leave request and updates its status."""
    update_doc = {
        "$set": {
            "status": new_status,
            f"{approver_role}_action_by": approver_id,
            f"{approver_role}_action_at": datetime.datetime.now(datetime.timezone.utc)
        }
    }
    if rejection_reason:
        update_doc["$set"]["rejection_reason"] = rejection_reason
        
    result = leave_requests_collection.update_one(
        {"_id": ObjectId(request_id)},
        update_doc
    )
    if result.modified_count > 0:
        return f"Request {request_id} has been successfully updated to {new_status}."
    return f"Failed to update request {request_id}."