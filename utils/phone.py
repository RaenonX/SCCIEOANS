from __future__ import annotations

from dataclasses import dataclass
from typing import Union, Generator


class PhoneCarriersManager:
    @staticmethod
    def get_carrier_by_name(telecom_name: str) -> Union[PhoneCarrier, None]:
        return _phone_carrier_dict.get(telecom_name)

    @staticmethod
    def get_carrier_generator() -> Generator[PhoneCarrier]:
        return (v for v in _phone_carrier_dict.values())


@dataclass
class PhoneCarrier:
    telecom_name: str
    mail_domain: str


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
