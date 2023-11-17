import re


class AccountInputFormatter:
    __LOWER_CASE_PATTERN = re.compile(r"[a-zа-я]")
    __UPPER_CASE_PATTERN = re.compile(r"[A-ZА-Я]")

    def format_phone_number(self, phone_number: str) -> str:
        if phone_number is None:
            return ""
        phone_number = phone_number.replace("-", "").replace(" ", "")
        if re.search(
            AccountInputFormatter.__LOWER_CASE_PATTERN, phone_number
        ) or re.search(AccountInputFormatter.__UPPER_CASE_PATTERN, phone_number):
            return phone_number
        if (
            not phone_number.startswith("+")
            and not phone_number.startswith("+8")
            and not phone_number.startswith("8")
        ):
            phone_number = f"+{phone_number}"
        if phone_number.startswith("8"):
            phone_number = f"+7{phone_number[1:]}"
        return phone_number
