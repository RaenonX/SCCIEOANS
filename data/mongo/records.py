from datetime import datetime
from typing import Union

from bson import ObjectId
from pymongo import DESCENDING

from config import DatabaseConfig
from ex import EnumWithName
from .base import BaseMongoCollection, DictLikeMapping

DATABASE_NAME = "records"


class AppointmentPurpose(EnumWithName):
    ACADEMIC_ADVISING = 1, "Academic Advising"


class AppointmentsManager:
    def __init__(self, mongo_client):
        self._scheduled = ScheduledRecords(mongo_client)
        self._appointments = AppointmentsRecords(mongo_client)

    def create_scheduled_appointment(
            self, student_id: int, purpose: AppointmentPurpose, scheduled_start: datetime, scheduled_end: datetime,
            advisor_id: Union[ObjectId, None] = None, notes: Union[str, None] = None) -> None:
        self._scheduled.create_scheduled_appointment(
            student_id, purpose, scheduled_start, scheduled_end, advisor_id, notes)

    def create_walkin_appointment(self, student_id: int, purpose: AppointmentPurpose,
                                  advisor_id: Union[ObjectId, None] = None, notes: Union[str, None] = None) -> None:
        self._appointments.create_appointment(student_id, purpose, advisor_id, notes)

    def check_in_from_scheduled(self, schedule_id: ObjectId) -> bool:
        sc = self._scheduled.get_scheduled_appointment(schedule_id)

        if sc is None:
            return False

        self._appointments.create_appointment_from_scheduled(sc)
        return True

    def get_scheduled_appointment(self, schedule_id: ObjectId) -> Union[ScheduledEntry, None]:
        return self._scheduled.get_scheduled_appointment(schedule_id)

    def get_waiting_appointments(self) -> Generator[AppointmentsEntry]:
        return self._appointments.get_waiting_appointments()

    def get_ongoing_appointments(self) -> Generator[AppointmentsEntry]:
        return self._appointments.get_ongoing_appointments()

    def update_meeting_start(self, appointment_id: ObjectId) -> None:
        self._appointments.update_appointment_start(appointment_id)

    def update_appointment_end(self, appointment_id: ObjectId) -> None:
        self._appointments.update_appointment_end(appointment_id)

    def remove_appointment(self, appointment_id: ObjectId) -> None:
        self._appointments.remove_record(appointment_id)


class ScheduledRecords(BaseMongoCollection):
    COLLECTION_NAME = "scheduled"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, DATABASE_NAME, ScheduledRecords.COLLECTION_NAME)
        self.create_index(ScheduledEntry.MEETING_START,
                          expireAfterSeconds=DatabaseConfig.SCHEDULED_APPOINTMENT_EXPIRATION_MINS * 60)

    def create_scheduled_appointment(
            self, student_id: int, purpose: AppointmentPurpose, scheduled_start: datetime, scheduled_end: datetime,
            advisor_id: Union[ObjectId, None] = None, notes: str = None) -> None:
        self.insert_one(ScheduledEntry.init(student_id, purpose, advisor_id, scheduled_start, scheduled_end, notes))

    def get_scheduled_appointment(self, schedule_id) -> Union[ScheduledEntry, None]:
        return ScheduledEntry.get_none(self.find_one({ScheduledEntry.ID: schedule_id}))


class AppointmentsRecords(BaseMongoCollection):
    COLLECTION_NAME = "appointments"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, DATABASE_NAME, AppointmentsRecords.COLLECTION_NAME)

    def create_appointment(
            self, student_id: int, purpose: AppointmentPurpose,
            advisor_id: Union[ObjectId, None] = None, notes: Union[str, None] = None) -> None:
        self.insert_one(AppointmentsEntry.init(student_id, purpose, advisor_id, notes))

    def create_appointment_from_scheduled(self, scheduled_entry: ScheduledEntry) -> None:
        self.insert_one(AppointmentsEntry.init_from_scheduled(scheduled_entry))

    def get_waiting_appointments(self) -> Generator[AppointmentsEntry]:
        return (AppointmentsEntry(x) for x in self.find({
            AppointmentsEntry.APPOINTMENT_START: {"$exists": False},
            AppointmentsEntry.APPOINTMENT_END: {"$exists": False}}).sort([ScheduledEntry.ID, DESCENDING]))

    def get_ongoing_appointments(self) -> Generator[AppointmentsEntry]:
        return (AppointmentsEntry(x) for x in self.find({
            AppointmentsEntry.APPOINTMENT_START: {"$exists": True},
            AppointmentsEntry.APPOINTMENT_END: {"$exists": False}}).sort([ScheduledEntry.ID, DESCENDING]))

    def update_appointment_start(self, appointment_id: ObjectId) -> None:
        self.update_one(
            {AppointmentsEntry.ID: appointment_id}, {AppointmentsEntry.APPOINTMENT_START: datetime.now()}, True)

    def update_appointment_end(self, appointment_id: ObjectId) -> None:
        self.update_one(
            {AppointmentsEntry.ID: appointment_id}, {AppointmentsEntry.APPOINTMENT_END: datetime.now()}, True)

    def remove_record(self, appointment_id: ObjectId) -> None:
        self.delete_one({AppointmentsEntry.ID: appointment_id})


class ScheduledEntry(DictLikeMapping):
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
    def init(student_id: int, purpose: AppointmentPurpose, advisor_id: Union[ObjectId, None],
             meeting_start: datetime, meeting_end: datetime, notes: Union[str, None] = None) -> ScheduledEntry:
        d = {
            ScheduledEntry.MEETING_START: meeting_start,
            ScheduledEntry.MEETING_END: meeting_end,
            ScheduledEntry.STUDENT_ID: student_id,
            ScheduledEntry.PURPOSE: purpose
        }

        if advisor_id is not None:
            d[ScheduledEntry.ADVISOR_ID] = advisor_id

        if notes is not None:
            d[ScheduledEntry.NOTES] = notes

        return ScheduledEntry(d)
        
    @property
    def id(self) -> ObjectId:
        return self[AppointmentsEntry.ID]

    @property
    def scheduled_timestamp(self) -> datetime:
        return ObjectId(self.id).generation_time

    @property
    def meeting_start(self) -> datetime:
        return self[ScheduledEntry.MEETING_START]
    
    @property
    def meeting_end(self) -> datetime:
        return self[ScheduledEntry.MEETING_END]
    
    @property
    def student_id(self) -> int:
        return self[ScheduledEntry.STUDENT_ID]
    
    @property
    def purpose(self) -> AppointmentPurpose:
        return AppointmentPurpose(self[ScheduledEntry.PURPOSE])
    
    @property
    def advisor_id(self) -> ObjectId:
        return self[ScheduledEntry.ADVISOR_ID]

    @property
    def advisor_specified(self) -> bool:
        return ScheduledEntry.ADVISOR_ID in self and self[ScheduledEntry.ADVISOR_ID] is not None

    @property
    def notes(self) -> str:
        return self.get(ScheduledEntry.NOTES, "")


class AppointmentsEntry(DictLikeMapping):
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
    def init(sid: int, purpose: AppointmentPurpose, advisor_id: Union[ObjectId, None] = None,
             notes: Union[str, None] = None, scheduled: Union[ScheduledEntry, None] = None) -> AppointmentsEntry:
        d = {
            AppointmentsEntry.STUDENT_ID: sid,
            AppointmentsEntry.PURPOSE: purpose,
            AppointmentsEntry.NOTES: notes
        }

        if advisor_id is not None:
            d[AppointmentsEntry.ADVISOR_ID] = advisor_id

        if scheduled is not None:
            d[AppointmentsEntry.SCHEDULED] = scheduled

        return AppointmentsEntry(d)

    @staticmethod
    def init_from_scheduled(scheduled: ScheduledEntry) -> AppointmentsEntry:
        d = {
            AppointmentsEntry.ADVISOR_ID: scheduled.advisor_id,
            AppointmentsEntry.STUDENT_ID: scheduled.student_id,
            AppointmentsEntry.PURPOSE: scheduled.purpose,
            AppointmentsEntry.NOTES: scheduled.notes,
            AppointmentsEntry.SCHEDULED: AppointmentsEntrySchedule.init(
                scheduled.meeting_start, scheduled.meeting_end, scheduled.scheduled_timestamp)
        }

        return AppointmentsEntry(d)

    @property
    def id(self) -> ObjectId:
        return self[AppointmentsEntry.ID]

    @property
    def scheduled(self) -> Union[AppointmentsEntrySchedule, None]:
        if AppointmentsEntry.SCHEDULED in self:
            return AppointmentsEntrySchedule(self[AppointmentsEntry.SCHEDULED])
        else:
            return None

    @property
    def lined_up_timestamp(self) -> datetime:
        return ObjectId(self.id).generation_time

    @property
    def meeting_start(self) -> Union[datetime, None]:
        return self.get(AppointmentsEntry.APPOINTMENT_START)
    
    @property
    def meeting_end(self) -> Union[datetime, None]:
        return self.get(AppointmentsEntry.APPOINTMENT_END)
    
    @property
    def student_id(self) -> int:
        return self[AppointmentsEntry.STUDENT_ID]
    
    @property
    def purpose(self) -> AppointmentPurpose:
        return AppointmentPurpose(self[AppointmentsEntry.PURPOSE])
    
    @property
    def advisor_id(self) -> Union[ObjectId, None]:
        return self[AppointmentsEntry.ADVISOR_ID]

    @property
    def advisor_specified(self) -> bool:
        return AppointmentsEntry.ADVISOR_ID in self and self[AppointmentsEntry.ADVISOR_ID] is not None

    @property
    def notes(self) -> str:
        return self[AppointmentsEntry.NOTES]


class AppointmentsEntrySchedule(DictLikeMapping):
    SCHEDULED_TS = "s_ts"
    SCHEDULED_START = "s_start"
    SCHEDULED_END = "s_end"

    def __init__(self, org_dict):
        if AppointmentsEntrySchedule.SCHEDULED_TS not in org_dict:
            org_dict[AppointmentsEntrySchedule.SCHEDULED_TS] = datetime.now()

        super().__init__(org_dict)

    @staticmethod
    def init(
            schedule_start: datetime, schedule_end: datetime,
            scheduled_timestamp: Union[datetime, None] = None) -> AppointmentsEntrySchedule:
        d = {
            AppointmentsEntrySchedule.SCHEDULED_START: schedule_start,
            AppointmentsEntrySchedule.SCHEDULED_END: schedule_end
        }

        if scheduled_timestamp is not None:
            d[AppointmentsEntrySchedule.SCHEDULED_TS] = scheduled_timestamp

        return AppointmentsEntrySchedule(d)

    @property
    def start(self) -> datetime:
        return self[AppointmentsEntrySchedule.SCHEDULED_START]

    @property
    def end(self) -> datetime:
        return self[AppointmentsEntrySchedule.SCHEDULED_END]

    @property
    def timestamp(self) -> Union[datetime, None]:
        return self.get(AppointmentsEntrySchedule.SCHEDULED_TS)
