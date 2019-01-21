from typing import Union

from data import Language, languages
from utils.phone import PhoneCarrier, PhoneCarriersManager
from .base import BaseMongoCollection, DictLikeMapping

DATABASE_NAME = "accounts"


class StudentInfoManager(BaseMongoCollection):
    COLLECTION_NAME = "student_info"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, DATABASE_NAME, StudentInfoManager.COLLECTION_NAME)
        self.create_index(StudentInfoEntry.STUDENT_ID, unique=True)

    def create_student_info_entry(
            self, student_id: int, lang_id: int, email: str,
            phone_number: Union[str, None] = None, phone_carrier_name: Union[str, None] = None,
            name_pronunciation: Union[str, None] = None,
            notif_sms: bool = False, notif_email: bool = False, notif_manual: bool = True) -> None:
        self.insert_one(
            StudentInfoEntry.init(
                student_id, lang_id, email, phone_number, phone_carrier_name, name_pronunciation,
                notif_sms, notif_email, notif_manual))

    def is_student_id_exists(self, student_id: Union[int, None]) -> bool:
        if student_id is None:
            return False

        return self.count_documents({StudentInfoEntry.STUDENT_ID: student_id}) > 0


class StudentInfoEntry(DictLikeMapping):
    STUDENT_ID = "sid"

    NAME_PRONUNCIATION = "name_prn"

    LANGUAGE_ID = "lang"
    PHONE = "ph"
    EMAIL = "email"
    NOTIFICATION_PREFERENCES = "notif"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(sid: int, lang_id: int, email: Union[str, None] = None,
             phone_number: Union[str, None] = None, phone_carrier_name: Union[str, None] = None,
             name_pronunciation: Union[str, None] = None,
             notif_sms: bool = False, notif_email: bool = False, notif_manual: bool = True) -> StudentInfoEntry:

        d = {
            StudentInfoEntry.STUDENT_ID: sid,
            StudentInfoEntry.NAME_PRONUNCIATION: name_pronunciation,
            StudentInfoEntry.LANGUAGE_ID: lang_id,
            StudentInfoEntry.NOTIFICATION_PREFERENCES:
                StudentEntryNotificationPreference.init(notif_sms, notif_email, notif_manual)
        }

        if email is not None:
            d[StudentInfoEntry.EMAIL] = email

        if phone_number is not None or phone_carrier_name is not None:
            d[StudentInfoEntry.PHONE] = StudentEntryPhone.init(phone_number, phone_carrier_name)

        return StudentInfoEntry(d)

    @property
    def student_id(self) -> str:
        return self[StudentInfoEntry.STUDENT_ID]

    @property
    def name_pronunciation(self) -> str:
        return self[StudentInfoEntry.NAME_PRONUNCIATION]

    @property
    def language(self) -> Language:
        return languages[self[StudentInfoEntry.LANGUAGE_ID]]

    @property
    def phone(self) -> Union[StudentEntryPhone, None]:
        ret = self.get(StudentInfoEntry.PHONE)
        return StudentEntryPhone(ret) if ret is not None else None

    @property
    def email(self) -> Union[str, None]:
        return self.get(StudentInfoEntry.EMAIL)

    @property
    def notification_preferences(self) -> StudentEntryNotificationPreference:
        return StudentEntryNotificationPreference(self[StudentInfoEntry.NOTIFICATION_PREFERENCES])


class StudentEntryPhone(DictLikeMapping):
    PHONE_NUMBER = "num"
    PHONE_CARRIER = "cr"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(num: str, carrier: str) -> StudentEntryPhone:
        d = {
            StudentEntryPhone.PHONE_NUMBER: num,
            StudentEntryPhone.PHONE_CARRIER: carrier
        }

        return StudentEntryPhone(d)

    @property
    def phone_number(self) -> str:
        return self[StudentEntryPhone.PHONE_NUMBER]

    @property
    def phone_carrier(self) -> PhoneCarrier:
        return PhoneCarriersManager.get_carrier_by_name(self[StudentEntryPhone.PHONE_CARRIER])


class StudentEntryNotificationPreference(DictLikeMapping):
    SMS = "sms"
    EMAIL = "email"
    MANUAL = "manual"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(sms: bool = False, email: bool = False, manual: bool = False):
        d = {
            StudentEntryNotificationPreference.SMS: sms,
            StudentEntryNotificationPreference.EMAIL: email,
            StudentEntryNotificationPreference.MANUAL: manual
        }

        return StudentEntryNotificationPreference(d)

    @property
    def sms(self) -> bool:
        return self[StudentEntryNotificationPreference.SMS]

    @property
    def email(self) -> bool:
        return self[StudentEntryNotificationPreference.EMAIL]

    @property
    def manual(self) -> bool:
        return self[StudentEntryNotificationPreference.MANUAL]
