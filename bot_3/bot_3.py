from collections import UserDict
from datetime import datetime, date, timedelta

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Error: Contact not found."
        except ValueError as ve:
            return f"Error: {str(ve)}"
        except IndexError:
            return "Error: Missing arguments."
        except Exception as e:
            return f"Error: {str(e)}"
    return inner

def parse_input(user_input):
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

class Field:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be exactly 10 digits and contain only numbers")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        if isinstance(value, date):
            self.value = value
        else:
            try:
                self.value = datetime.strptime(value, "%d.%m.%Y").date()
            except Exception:
                raise ValueError("Birthday must be in format DD.MM.YYYY")
    
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number: str):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number: str):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
            return True
        return False

    def edit_phone(self, old_number: str, new_number: str):
        phone = self.find_phone(old_number)
        if phone:
            Phone(new_number) 
            phone.value = new_number
            return True
        raise ValueError("Old phone number not found")

    def find_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_str_or_date):
        self.birthday = Birthday(birthday_str_or_date)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        b = self.birthday.value
        try_year = today.year
        def next_valid(year):
            try:
                return date(year=year, month=b.month, day=b.day)
            except ValueError:
                return None
        next_bd = next_valid(try_year)
        if not next_bd or next_bd < today:
            ny = try_year + 1
            while True:
                candidate = next_valid(ny)
                if candidate:
                    next_bd = candidate
                    break
                ny += 1
        delta = (next_bd - today).days
        return delta

    def __str__(self):
        phones = ", ".join([p.value for p in self.phones]) if self.phones else "—"
        bd = self.birthday.__str__() if self.birthday else "—"
        return f"{self.name.value}: {phones} | Birthday: {bd}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def add_contact(self, name: str, phone: str):
        if name in self.data:
            rec = self.data[name]
            rec.add_phone(phone)
        else:
            rec = Record(name)
            rec.add_phone(phone)
            self.add_record(rec)

    def change_contact(self, name: str, phone: str):
        if name not in self.data:
            raise KeyError("Contact not found.")
        rec = self.data[name]
        if rec.phones:
            Phone(phone) 
            rec.phones[0].value = phone
        else:
            rec.add_phone(phone)

    def get_phone(self, name: str) -> str:
        if name not in self.data:
            raise KeyError("Contact not found.")
        rec = self.data[name]
        if not rec.phones:
            return "No phones set for this contact."
        return ", ".join([p.value for p in rec.phones])

    def all_contacts(self):
        return {name: {'phones': [p.value for p in rec.phones], 'birthday': (rec.birthday.value if rec.birthday else None)}
                for name, rec in self.data.items()}

    def add_birthday(self, name: str, bday: date):
        if name not in self.data:
            raise KeyError("Contact not found.")
        self.data[name].add_birthday(bday)

    def get_birthday(self, name: str):
        if name not in self.data:
            raise KeyError("Contact not found.")
        b = self.data[name].birthday
        if not b:
            raise ValueError("Birthday not set for this contact.")
        return b.value

    def upcoming_birthdays(self, days_ahead: int = 7):
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        result = {}
        uk_weekdays = ['Понеділок','Вівторок','Середа','Четвер',"П'ятниця",'Субота','Неділя']

        for name, rec in self.data.items():
            b = rec.birthday.value if rec.birthday else None
            if not b:
                continue
            try:
                next_bday = date(year=today.year, month=b.month, day=b.day)
            except ValueError:
                ny = today.year
                next_bday = None
                while True:
                    ny += 1
                    try:
                        next_bday = date(year=ny, month=b.month, day=b.day)
                        break
                    except ValueError:
                        continue

            if next_bday < today:
                ny = today.year + 1
                while True:
                    try:
                        next_bday = date(year=ny, month=b.month, day=b.day)
                        break
                    except ValueError:
                        ny += 1

            if today <= next_bday <= end_date:
                weekday_name = uk_weekdays[next_bday.weekday()]
                result.setdefault(weekday_name, []).append((name, next_bday))

        for wd in result:
            result[wd].sort(key=lambda x: x[1])
        return result

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join([str(rec) for rec in self.data.values()])

@input_error
def add_contact_cmd(args, book: AddressBook):
    if len(args) != 2:
        return "Error: Invalid number of arguments for 'add' command. Use: add [name] [phone]"
    name, phone = args
    book.add_contact(name, phone)
    return "Contact added."

@input_error
def change_contact_cmd(args, book: AddressBook):
    if len(args) != 2:
        return "Error: Invalid number of arguments for 'change' command. Use: change [name] [phone]"
    name, phone = args
    book.change_contact(name, phone)
    return "Contact updated."

@input_error
def show_phone_cmd(args, book: AddressBook):
    if len(args) != 1:
        return "Error: Invalid number of arguments for 'phone' command. Use: phone [name]"
    name = args[0]
    return book.get_phone(name)

def show_all_contacts(book: AddressBook):
    data = book.all_contacts()
    if not data:
        return "No contacts found."
    result = "All contacts:\n"
    for name, info in data.items():
        phones = ", ".join(info.get('phones', [])) if info.get('phones') else "—"
        b = info.get('birthday')
        bstr = b.strftime("%d.%m.%Y") if b else "—"
        result += f"{name}: {phones} | Birthday: {bstr}\n"
    return result.strip()

@input_error
def add_birthday_cmd(args, book: AddressBook):
    if len(args) != 2:
        return "Error: Invalid number of arguments for 'add-birthday'. Use: add-birthday [name] [DD.MM.YYYY]"
    name, bstr = args
    try:
        bdate = datetime.strptime(bstr, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Birthday must be in DD.MM.YYYY format.")
    book.add_birthday(name, bdate)
    return "Birthday added."

@input_error
def show_birthday_cmd(args, book: AddressBook):
    if len(args) != 1:
        return "Error: Invalid number of arguments for 'show-birthday'. Use: show-birthday [name]"
    name = args[0]
    b = book.get_birthday(name)
    return b.strftime("%d.%m.%Y")

@input_error
def birthdays_cmd(args, book: AddressBook):
    if len(args) not in (0, 1):
        return "Error: Invalid arguments for 'birthdays'. Use: birthdays [days_optional]"
    days = 7
    if len(args) == 1:
        if not args[0].isdigit():
            raise ValueError("days argument must be an integer.")
        days = int(args[0])
    upcoming = book.upcoming_birthdays(days_ahead=days)
    if not upcoming:
        return "No birthdays in the upcoming period."
    lines = []
    for weekday, items in upcoming.items():
        lines.append(f"{weekday}:")
        for name, dt in items:
            lines.append(f"  - {name}: {dt.strftime('%d.%m')}")
    return "\n".join(lines)

def main():
    book = AddressBook()
    print("Welcome to the Contact Bot (combined AddressBook)!")
    print("Commands: add, change, phone, all, add-birthday, show-birthday, birthdays, hello, close/exit/good bye")

    while True:
        user_input = input("enter command: ")
        command, args = parse_input(user_input)

        if command == "":
            print("Error: Please enter a command.")
            continue

        if command in ["close", "exit", "good", "goodbye", "good-bye", "good bye"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact_cmd(args, book))
        elif command == "change":
            print(change_contact_cmd(args, book))
        elif command == "phone":
            print(show_phone_cmd(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday_cmd(args, book))
        elif command == "show-birthday":
            print(show_birthday_cmd(args, book))
        elif command == "birthdays":
            print(birthdays_cmd(args, book))
        else:
            print("Error: Unknown command.")

if __name__ == "__main__":
    main()