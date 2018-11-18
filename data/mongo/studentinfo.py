from .base import base_collection, dict_like_mapping

DATABASE_NAME = "accounts"

class student_info_manager(base_collection):
    COLLECTION_NAME = "student_info"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, DATABASE_NAME, student_info_manager.COLLECTION_NAME)
        self.create_index(student_info_entry.STUDENT_ID, unique=True)

    def create_student_info_entry(self, student_id, languages, emails=[], phone_number=None, phone_carrier=None, name_pronunciation=None,
             notif_sms=False, notif_email=False, notif_manual=True):
        self.insert_one(student_info_entry.init(student_id, languages, emails, phone_number, phone_carrier, name_pronunciation, notif_sms, notif_email, notif_manual))

class student_info_entry(dict_like_mapping):
    STUDENT_ID = "sid"

    NAME_PRONUNCIATION = "name_prn"

    LANGUAGES = "lang"
    PHONE = "ph"
    EMAILS = "emails"
    NOTIFICATION_PREFERENCES = "notif"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(sid, languages, emails=[], phone_number=None, phone_carrier=None, name_pronunciation=None,
             notif_sms=False, notif_email=False, notif_manual=True):
        if not isinstance(languages, list):
            languages = [languages]

        if not isinstance(emails, list):
            emails = [emails]

        d = {
            student_info_entry.STUDENT_ID: sid,
            student_info_entry.NAME_PRONUNCIATION: name_pronunciation,
            student_info_entry.LANGUAGES: languages,
            student_info_entry.EMAILS: emails,
            student_info_entry.NOTIFICATION_PREFERENCES: student_entry_notification_pref.init(notif_sms, notif_email, notif_manual)
        }

        if phone_number is not None or phone_carrier is not None:
            d[student_info_entry.PHONE] = student_entry_phone.init(phone_number, phone_carrier)

        return student_info_entry(d)

    @property
    def student_id(self):
        return self[student_info_entry.STUDENT_ID]

    @property
    def name_pronunciation(self):
        return self[student_info_entry.NAME_PRONUNCIATION]

    @property
    def languages(self):
        return self[student_info_entry.LANGUAGES]

    @property
    def phone(self):
        ret = self.get(student_info_entry.PHONE)
        return student_entry_phone(ret) if ret is not None else None

    @property
    def emails(self):
        return self[student_info_entry.EMAILS]

    @property
    def notification_preferences(self):
        return student_entry_notification_pref(self[student_info_entry.NOTIFICATION_PREFERENCES])

class student_entry_phone(dict_like_mapping):
    PHONE_NUMBER = "num"
    PHONE_CARRIER = "cr"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(num, carrier):
        d = {
            student_entry_phone.PHONE_NUMBER: num,
            student_entry_phone.PHONE_CARRIER: carrier
        }

        return student_entry_phone(d)

    @property
    def phone_number(self):
        return self[student_entry_phone.PHONE_NUMBER]

    @property
    def phone_carrier(self):
        return self[student_entry_phone.PHONE_CARRIER]

class student_entry_notification_pref(dict_like_mapping):
    SMS = "sms"
    EMAIL = "email"
    MANUAL = "manual"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init(sms=False, email=False, manual=False):
        d = {
            student_entry_notification_pref.SMS: sms,
            student_entry_notification_pref.EMAIL: email,
            student_entry_notification_pref.MANUAL: manual
        }

        return student_entry_notification_pref(d)

    @property
    def sms(self):
        return self[student_entry_notification_pref.SMS]

    @property
    def email(self):
        return self[student_entry_notification_pref.EMAIL]

    @property
    def manual(self):
        return self[student_entry_notification_pref.MANUAL]