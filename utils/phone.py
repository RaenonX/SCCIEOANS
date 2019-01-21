from typing import Union, Generator

# noinspection PyUnboundLocalVariable,PyUnresolvedReferences
_phone_carrier_dict = {
    "Alltel": PhoneCarrier("Alltel", "message.alltel.com"),
    "AT&T": PhoneCarrier("AT&T", "txt.att.net"),
    "T-Mobile": PhoneCarrier("T-Mobile", "tmomail.net"),
    "Virgin Mobile": PhoneCarrier("Virgin Mobile", "vmobl.com"),
    "Sprint": PhoneCarrier("Sprint", "messaging.sprintpcs.com"),
    "Verizon": PhoneCarrier("Verizon", "vtext.com"),
    "Nextel": PhoneCarrier("Nextel", "messaging.nextel.com"),
    "US Cellular": PhoneCarrier("US Cellular", "mms.uscc.net")
}


class PhoneCarriersManager:
    @staticmethod
    def get_carrier_by_name(telecom_name: str) -> Union[PhoneCarrier, None]:
        return _phone_carrier_dict.get(telecom_name)

    @staticmethod
    def get_carrier_generator() -> Generator[PhoneCarrier]:
        return (v for k, v in _phone_carrier_dict)


class PhoneCarrier:
    def __init__(self, telecom_name: str, mail_domain: str):
        self._name = telecom_name
        self._domain = mail_domain

    @property
    def telecom_name(self) -> str:
        return self._name

    @property
    def mail_domain(self) -> str:
        return self.mail_domain
