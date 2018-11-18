from datetime import datetime

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from ex import EnumWithName
from config import DatabaseConfig

from .base import base_collection, dict_like_mapping

DATABASE_NAME = "records"

class AppointmentPurpose(EnumWithName):
    ACADEMIC_ADVISING = 1, "Academic Advising"

class records_manager:
    def __init__(self, mongo_client):
        self._scheduled = scheduled_records(mongo_client)
        self._appointments = appointments_records(mongo_client)

    def create_scheduled_appointment(self, student_id, purpose, advisor_id, scheduled_start, scheduled_end, notes=None):
        self._scheduled.create_scheduled_appointment(student_id, purpose, advisor_id, scheduled_start, scheduled_end, notes)

    def create_walkin_appointment(self, student_id, purpose, advisor_id=None, notes=None):
        self._appointments.create_appointment(student_id, purpose, advisor_id, notes)

    def check_in_from_scheduled(self, schedule_id):
        """
        Return:
            True if succeed, otherwise, False.
        """
        sc = self._scheduled.get_scheduled_appointment(schedule_id)

        if sc is None:
            return False

        self._appointments.create_appointment_from_scheduled(sc)
        return True

    def get_scheduled_appointment(self, schedule_id):
        """
        Return:
            Return scheduled_entry if the document is present. Otherwise, return None.
        """
        return self._scheduled.get_scheduled_appointment(schedule_id)

    def get_waiting_appointments(self):
        return self._appointments.get_waiting_appointments()

    def get_ongoing_appointments(self):
        return self._appointments.get_ongoing_appointments()

    def update_meeting_start(self, appointment_id):
        self._appointments.update_appointment_start(appointment_id)

    def update_appointment_end(self, appointment_id):
        self._appointments.update_appointment_end(appointment_id)

    def remove_appointment(self, appointment_id):
        self._appointments.remove_record(appointment_id)

class scheduled_records(base_collection):
    COLLECTION_NAME = "scheduled"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, DATABASE_NAME, scheduled_records.COLLECTION_NAME)
        self.create_index(scheduled_entry.MEETING_START, expireAfterSeconds=DatabaseConfig.SCHEDULED_APPOINTMENT_EXPIRATION_MINS * 60)

    def create_scheduled_appointment(self, student_id, purpose, advisor_id, scheduled_start, scheduled_end, notes=None):
        self.insert_one(scheduled_entry.init(student_id, purpose, advisor_id, scheduled_start, scheduled_end, notes))

    def get_scheduled_appointment(self, schedule_id):
        """
        Return:
            Return scheduled_entry if the document is present. Otherwise, return None.
        """
        ret = self.find_one({ scheduled_entry.ID: schedule_id })
        return scheduled_entry(ret) if ret is not None else None

class appointments_records(base_collection):
    COLLECTION_NAME = "appointments"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, DATABASE_NAME, appointments_records.COLLECTION_NAME)

    def create_appointment(self, student_id, purpose, advisor_id=None, notes=None):
        self.insert_one(appointments_entry.init(student_id, purpose, advisor_id, notes))

    def create_appointment_from_scheduled(self, schedule_record):
        self.insert_one(appointments_entry.init_from_scheduled(schedule_record))

    def get_waiting_appointments(self):
        return self.find({ 
            appointments_entry.APPOINTMENT_START: { "$exists": False }, 
            appointments_entry.APPOINTMENT_END: { "$exists": False } }).sort([scheduled_entry.ID, DESCENDING])

    def get_ongoing_appointments(self):
        return self.find({ 
            appointments_entry.APPOINTMENT_START: { "$exists": True }, 
            appointments_entry.APPOINTMENT_END: { "$exists": False } }).sort([scheduled_entry.ID, DESCENDING])

    def update_appointment_start(self, appointment_id):
        self.update_one({ appointments_entry.ID: appointment_id }, { appointments_entry.APPOINTMENT_START: datetime.now() }, True)

    def update_appointment_end(self, appointment_id):
        self.update_one({ appointments_entry.ID: appointment_id }, { appointments_entry.APPOINTMENT_END: datetime.now() }, True)

    def remove_record(self, data_id):
        self.delete_one({ appointments_entry.ID: data_id })

class scheduled_entry(dict_like_mapping):
    ID = "_id"
    
    MEETING_START = "m_start"
    MEETING_END = "m_end"
    STUDENT_ID = "sid"
    PURPOSE = "pps"
    ADVISOR_ID = "adv_id"
    NOTES = "n"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(student_id, purpose, advisor_id, meeting_start, meeting_end, notes=None):
        d = {
            scheduled_entry.MEETING_START: meeting_start,
            scheduled_entry.MEETING_END: meeting_end,
            scheduled_entry.STUDENT_ID: student_id,
            scheduled_entry.PURPOSE: purpose,
            scheduled_entry.ADVISOR_ID: advisor_id
        }

        if notes is not None:
            d[scheduled_entry.NOTES] = notes

        return scheduled_entry(d)
        
    @property
    def id(self):
        return self[appointments_entry.ID]

    @property
    def scheduled_timestamp(self):
        return ObjectId(self.id).generation_time

    @property
    def meeting_start(self):
        return self[scheduled_entry.MEETING_START]
    
    @property
    def meeting_end(self):
        return self[scheduled_entry.MEETING_END]
    
    @property
    def student_id(self):
        return self[scheduled_entry.STUDENT_ID]
    
    @property
    def purpose(self):
        return AppointmentPurpose(self[scheduled_entry.PURPOSE])
    
    @property
    def advisor_id(self):
        return self[scheduled_entry.ADVISOR_ID]

    @property
    def advisor_specified(self):
        return scheduled_entry.ADVISOR_ID in self

    @property
    def notes(self):
        return self[scheduled_entry.NOTES]

class appointments_entry(dict_like_mapping):
    ID = "_id"
    
    SCHEDULED = "scheduled"

    APPOINTMENT_START = "a_start"
    APPOINTMENT_END = "a_end"
    STUDENT_ID = "sid"
    PURPOSE = "pps"
    ADVISOR_ID = "adv_id"
    NOTES = "n"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(sid, purpose, advisor_id=None, notes=None, scheduled=None):
        d = {
            appointments_entry.STUDENT_ID: sid,
            appointments_entry.PURPOSE: purpose,
            appointments_entry.NOTES: notes
        }

        if advisor is not None:
            d[appointments_entry.ADVISOR_ID] = advisor_id

        if scheduled is not None:
            d[appointments_entry.SCHEDULED] = scheduled

        return appointments_entry(d)

    @staticmethod
    def init_from_scheduled(scheduled):
        d = {
            appointments_entry.ADVISOR_ID: scheduled.advisor_id,
            appointments_entry.STUDENT_ID: scheduled.student_id,
            appointments_entry.PURPOSE: scheduled.purpose,
            appointments_entry.NOTES: scheduled.notes,
            appointments_entry.SCHEDULED: appointments_entry_schedule.init(
                scheduled.meeting_start, scheduled.meeting_end, scheduled.scheduled_timestamp)
        }

        return appointments_entry(d)

    @property
    def id(self):
        return self[appointments_entry.ID]

    @property
    def scheduled(self):
        if appointments_entry.SCHEDULED in self:
            return appointments_entry_schedule(self[appointments_entry.SCHEDULED])
        else:
            return None

    @property
    def lined_up_timestamp(self):
        return ObjectId(self.id).generation_time

    @property
    def meeting_start(self):
        return self.get(appointments_entry.APPOINTMENT_START)
    
    @property
    def meeting_end(self):
        return self.get(appointments_entry.APPOINTMENT_END)
    
    @property
    def student_id(self):
        return self[appointments_entry.STUDENT_ID]
    
    @property
    def purpose(self):
        return AppointmentPurpose(self[appointments_entry.PURPOSE])
    
    @property
    def advisor_id(self):
        return self[appointments_entry.ADVISOR_ID]

    @property
    def advisor_specified(self):
        return appointments_entry.ADVISOR_ID in self

    @property
    def notes(self):
        return self[appointments_entry.NOTES]

class appointments_entry_schedule(dict_like_mapping):
    SCHEDULED_TS = "s_ts"
    SCHEDULED_START = "s_start"
    SCHEDULED_END = "s_end"

    def __init__(self, org_dict):
        if appointments_entry_schedule.SCHEDULED_TS not in org_dict:
            org_dict[appointments_entry_schedule.SCHEDULED_TS] = datetime.now()

        super().__init__(org_dict)

    @staticmethod
    def init(schedule_start, schedule_end, scheduled_timestamp=None):
        d = {
            appointments_entry_schedule.SCHEDULED_START: schedule_start,
            appointments_entry_schedule.SCHEDULED_END: schedule_end
        }

        if scheduled_timestamp is not None:
            d[appointments_entry_schedule.SCHEDULED_TS] = scheduled_timestamp

        return appointments_entry_schedule(d)

    @property
    def start(self):
        return self[appointments_entry_schedule.SCHEDULED_START]

    @property
    def end(self):
        return self[appointments_entry_schedule.SCHEDULED_END]

    @property
    def timestamp(self):
        return self[appointments_entry_schedule.SCHEDULED_TS]