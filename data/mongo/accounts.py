import uuid
import hashlib

from ex import EnumWithName

from .base import base_collection, dict_like_mapping

DATABASE_NAME = "accounts"

SESSION_LOGIN_KEY = "lgn_key"

class Identity(EnumWithName):
    STUDENT = 1, "Student"
    ADVISOR = 2, "Advisor"
    STAFF = 3, "Staff"

class account_manager(base_collection):
    COLLECTION_NAME = "accounts"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, DATABASE_NAME, account_manager.COLLECTION_NAME)
        self.create_index(account_entry.ACCOUNT_ID, unique=True)
        self._login_key_cache = {}

    def get_account_by_login_key(self, login_key):
        """
        Return:
            Account in account_entry.
        """
        ret = self.find_one({ account_entry.LOGIN_KEY: login_key })
        return account_entry(ret) if ret is not None else None

    def create_account_student(self, account_id, name, student_id, password, recovery_email):
        """
        Return:
            The updated login key of the new account.
        """
        result = self.insert_one(account_entry.init_student(account_id, name, student_id, password, recovery_email))
        return self.update_login_key(result.inserted_id)

    def create_account_non_student(self, identity, account_id, name, password, recovery_email):
        """
        Return:
            The updated login key of the new account.
        """
        result = self.insert_one(account_entry.init_non_student(identity, name, account_id, password, recovery_email))
        return self.update_login_key(result.inserted_id)

    def is_account_id_exists(self, account_id):
        if account_id is None:
            return False

        return self.count({ account_entry.ACCOUNT_ID: account_id }) > 0

    def is_login_key_exists(self, login_key):
        """
        Return:
            The identity type in enum if exists, else return None.
        """
        if login_key in self._login_key_cache:
            return self._login_key_cache[login_key]
        else:
            result = self.find_one({ account_entry.LOGIN_KEY: login_key })
            if result is None:
                return None
            else:
                id_type = account_entry(result).identity
                self._login_key_cache[login_key] = id_type
                return id_type

    def update_login_key(self, account_serial_id):
        """
        Update the login key in the database and return the updated login key.
        """
        gen_key = self._random_login_key()
        entry = account_entry(self.find_one_and_update({ "_id": account_serial_id }, { "$set": { account_entry.LOGIN_KEY: gen_key } }, upsert=True))
        self._login_key_cache[gen_key] = entry.identity
        return gen_key

    def _random_login_key(self):
        return uuid.uuid4()

class account_entry(dict_like_mapping):
    IDENTITY = "i"

    ACCOUNT_ID = "aid"
    PASSWORD_SHA = "pw_sha"
    
    ACCOUNT_NAME = "name"
    RECOVERY_EMAIL = "r_mail"

    STUDENT_ID = "sid"
    LOGIN_KEY = "lg_key"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init_non_student(identity, name, account_id, password, recovery_email):
        return account_entry._init(identity, name, account_id, password, recovery_email)

    @staticmethod
    def init_student(account_id, name, student_id, password, recovery_email):
        return account_entry._init(Identity.STUDENT, name, account_id, password, recovery_email, student_id)

    @staticmethod
    def _init(identity, name, account_id, password, recovery_email, student_id=None):
        d = {
            account_entry.IDENTITY: identity,
            account_entry.ACCOUNT_NAME: name,
            account_entry.ACCOUNT_ID: account_id,
            account_entry.PASSWORD_SHA: to_sha256(password),
            account_entry.RECOVERY_EMAIL: recovery_email
        }

        if student_id is not None:
            d[account_entry.STUDENT_ID] = student_id

        return account_entry(d)
    
    @property 
    def identity(self):
        return Identity(self[account_entry.IDENTITY])
    
    @property 
    def account_id(self):
        return self[account_entry.ACCOUNT_ID]

    @property 
    def name(self):
        return self[account_entry.ACCOUNT_NAME]

    @property 
    def password_sha(self):
        return self[account_entry.PASSWORD_SHA]

    @property 
    def recovery_email(self):
        return self[account_entry.RECOVERY_EMAIL]

    @property 
    def student_id(self):
        return self.get(account_entry.STUDENT_ID)
    
    @property 
    def login_key(self):
        return self.get(account_entry.LOGIN_KEY)

def to_sha256(s):
    return hashlib.sha224(bytes(s, "utf-8")).hexdigest()