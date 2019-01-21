import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Union

import pymongo
from bson import ObjectId

from ex import EnumWithName
from .base import BaseMongoCollection, DictLikeMapping

DATABASE_NAME = "accounts"

SESSION_LOGIN_KEY = "lgn_key"


class Identity(EnumWithName):
    STUDENT = 1, "Student"
    ADVISOR = 2, "Advisor"
    STAFF = 3, "Staff"


class AccountManager(BaseMongoCollection):
    COLLECTION_NAME = "accounts"

    def __init__(self, mongo_client: pymongo.MongoClient):
        super().__init__(mongo_client, DATABASE_NAME, AccountManager.COLLECTION_NAME)
        self.create_index(AccountEntry.ACCOUNT_ID, unique=True)
        self._login_key_cache: dict = {}

    def get_account_by_login_key(self, login_key: str) -> Union[AccountEntry, None]:
        return AccountEntry.get_none(self.find_one({AccountEntry.LOGIN_KEY: login_key}))

    def get_account_by_recovery_email(self, recovery_email: str) -> Union[AccountEntry, None]:
        return AccountEntry.get_none(self.find_one({AccountEntry.RECOVERY_EMAIL: recovery_email}))

    def create_account_student(
            self, account_id: str, name: str,
            student_id: int, password: str, recovery_email: str) -> AccountEntry:
        result = self.insert_one(AccountEntry.init_student(account_id, name, student_id, password, recovery_email))
        return self.update_login_key(result.inserted_id)

    def create_account_non_student(
            self, identity: Identity, account_id: str, name: str, password: str, recovery_email: str) -> AccountEntry:
        result = self.insert_one(AccountEntry.init_non_student(identity, name, account_id, password, recovery_email))
        return self.update_login_key(result.inserted_id)

    def is_account_id_exists(self, account_id: str) -> bool:
        if account_id is None:
            return False

        return self.count_documents({AccountEntry.ACCOUNT_ID: account_id}) > 0

    def check_key_get_identity(self, login_key: str) -> Union[Identity, None]:
        if login_key in self._login_key_cache:
            return self._login_key_cache[login_key]
        else:
            result = self.find_one({AccountEntry.LOGIN_KEY: login_key})
            if result is None:
                return None
            else:
                id_type = AccountEntry(result).identity
                self._login_key_cache[login_key] = id_type
                return id_type

    def update_login_key(self, account_unique_id: ObjectId) -> AccountEntry:
        gen_key = AccountManager.random_login_key()
        entry = AccountEntry(self.find_one_and_update({AccountEntry.UNIQUE_ID: ObjectId(account_unique_id)},
                                                      {"$set": {AccountEntry.LOGIN_KEY: gen_key}},
                                                      return_document=pymongo.ReturnDocument.AFTER))
        self._login_key_cache[gen_key] = entry.identity
        return entry

    def login(self, account_id: str, account_pw: str) -> LoginResult:
        acc_entry = self.find_one(
            {AccountEntry.ACCOUNT_ID: account_id, AccountEntry.PASSWORD_SHA: to_sha256(account_pw)})

        if acc_entry is None:
            return LoginResult(False, None)
        else:
            return LoginResult(True, self.update_login_key(AccountEntry(acc_entry).unique_id))

    def reset_password(self, account_unique_id: str, account_pw: str) -> bool:
        return self.update_one({AccountEntry.UNIQUE_ID: ObjectId(account_unique_id)},
                               {"$set": {AccountEntry.PASSWORD_SHA: to_sha256(account_pw)}}).modified_count == 1

    @staticmethod
    def random_login_key() -> uuid:
        return uuid.uuid4()


class AccountEntry(DictLikeMapping):
    UNIQUE_ID = "_id"
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
    def init_non_student(
            identity: Identity, name: str, account_id: str, password: str, recovery_email: str) -> AccountEntry:
        return AccountEntry._init(identity, name, account_id, password, recovery_email)

    @staticmethod
    def init_student(
            account_id: str, name: str, student_id: int,
            password: str, recovery_email: str) -> AccountEntry:
        return AccountEntry._init(Identity.STUDENT, name, account_id, password, recovery_email, student_id)

    @staticmethod
    def _init(
            identity: Identity, name: str, account_id: str, password: str,
            recovery_email: str, student_id: Union[int, None] = None) -> AccountEntry:
        d = {
            AccountEntry.IDENTITY: identity,
            AccountEntry.ACCOUNT_NAME: name,
            AccountEntry.ACCOUNT_ID: account_id,
            AccountEntry.PASSWORD_SHA: to_sha256(password),
            AccountEntry.RECOVERY_EMAIL: recovery_email
        }

        if student_id is not None:
            d[AccountEntry.STUDENT_ID] = student_id

        return AccountEntry(d)
    
    @property
    def identity(self) -> Identity:
        return Identity(self[AccountEntry.IDENTITY])

    @property
    def unique_id(self) -> ObjectId:
        return self[AccountEntry.UNIQUE_ID]
    
    @property
    def account_id(self) -> str:
        return self[AccountEntry.ACCOUNT_ID]

    @property
    def name(self) -> str:
        return self[AccountEntry.ACCOUNT_NAME]

    @property
    def password_sha(self) -> str:
        return self[AccountEntry.PASSWORD_SHA]

    @property
    def recovery_email(self) -> str:
        return self[AccountEntry.RECOVERY_EMAIL]

    @property
    def student_id(self) -> Union[str, None]:
        return self.get(AccountEntry.STUDENT_ID)
    
    @property
    def login_key(self) -> Union[bytes, None]:
        return self.get(AccountEntry.LOGIN_KEY)


class PwLostTokenManager(BaseMongoCollection):
    COLLECTION_NAME = "pw_lost"
    EXPIRE_SECS = 86400

    def __init__(self, mongo_client: pymongo.MongoClient):
        super().__init__(mongo_client, DATABASE_NAME, PwLostTokenManager.COLLECTION_NAME)
        self.create_index(PwLostTokenEntry.CREATED_TIME, expireAfterSeconds=PwLostTokenManager.EXPIRE_SECS)
        self.create_index(PwLostTokenEntry.LINKED_ACCOUNT_UNIQUE_ID, unique=True)
        self._account_mgr = AccountManager(mongo_client)

    def create_and_get_entry(self, recovery_email: str) -> Union[PwLostTokenEntry, None]:
        acc_entry = self._account_mgr.get_account_by_recovery_email(recovery_email)

        if acc_entry is not None:
            return PwLostTokenEntry(self.find_one_and_update(
                {PwLostTokenEntry.LINKED_ACCOUNT_UNIQUE_ID: acc_entry.unique_id},
                {"$set": {
                    PwLostTokenEntry.CREATED_TIME: datetime.now(),
                    PwLostTokenEntry.TOKEN: PwLostTokenManager.generate_token()}},
                upsert=True,
                return_document=pymongo.ReturnDocument.AFTER))
        else:
            return None

    def get_entry(self, token: str) -> Union[PwLostTokenEntry, None]:
        return PwLostTokenEntry.get_none(self.find_one({PwLostTokenEntry.TOKEN: token}))

    def delete_entry(self, token: str) -> Union[PwLostTokenEntry, None]:
        return PwLostTokenEntry.get_none(self.find_one_and_delete({PwLostTokenEntry.TOKEN: token}))

    @staticmethod
    def generate_token() -> str:
        return str(uuid.uuid4())


class PwLostTokenEntry(DictLikeMapping):
    CREATED_TIME = "ct"
    LINKED_ACCOUNT_UNIQUE_ID = "auid"
    TOKEN = "t"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def created_time(self) -> datetime:
        return self[PwLostTokenEntry.CREATED_TIME]

    @property
    def linked_account_unique_id(self) -> ObjectId:
        return self[PwLostTokenEntry.LINKED_ACCOUNT_UNIQUE_ID]

    @property
    def token(self) -> str:
        return self[PwLostTokenEntry.TOKEN]

    def get_html_content(self, reset_pw_url: str) -> str:
        return f"Use the link below to reset your password:\n" \
            f"<a href={reset_pw_url}>{reset_pw_url}</a>\n" \
            f"\n" \
            f"The link will expired on " \
            f"{(self.created_time + timedelta(seconds=PwLostTokenManager.EXPIRE_SECS)):%Y/%m/%d %H:%M:%S}."


class LoginResult:
    def __init__(self, success: bool, account_entry: Union[AccountEntry, None]):
        self._success = success
        self._acc_entry = account_entry

    @property
    def success(self) -> bool:
        return self._success

    @property
    def acc_entry(self) -> Union[AccountEntry, None]:
        return self._acc_entry


def to_sha256(s: str) -> str:
    return hashlib.sha224(bytes(s, "utf-8")).hexdigest()
