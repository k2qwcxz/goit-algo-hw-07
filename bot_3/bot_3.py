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

class AddressBook:
    def __init__(self):
        self._data = {}

    def add_contact(self, name: str, phone: str):
        if not phone.isdigit():
            raise ValueError("Phone must contain only digits.")
        self._data[name] = {'phone': phone, 'birthday': None}

    def change_contact(self, name: str, phone: str):
        if not phone.isdigit():
            raise ValueError("Phone must contain only digits.")
        if name not in self._data:
            raise KeyError("Contact not found.")
        self._data[name]['phone'] = phone

    def get_phone(self, name: str) -> str:
        if name not in self._data:
            raise KeyError("Contact not found.")
        return self._data[name]['phone']

    def all_contacts(self):
        return {name: info.copy() for name, info in self._data.items()}

    def add_birthday(self, name: str, bday: date):
        if name not in self._data:
            raise KeyError("Contact not found.")
        self._data[name]['birthday'] = bday

    def get_birthday(self, name: str):
        if name not in self._data:
            raise KeyError("Contact not found.")
        b = self._data[name]['birthday']
        if not b:
            raise ValueError("Birthday not set for this contact.")
        return b

    def upcoming_birthdays(self, days_ahead: int = 7):
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        result = {} 
        uk_weekdays = ['Понеділок','Вівторок','Середа','Четвер',"П'ятниця",'Субота','Неділя']

        for name, info in self._data.items():
            b = info.get('birthday')
            if not b:
                continue
            try:
                next_bday = date(year=today.year, month=b.month, day=b.day)
            except ValueError:
                ny = today.year
                while True:
                    ny += 1
                    try:
                        next_bday = date(year=ny, month=b.month, day=b.day)
                        break
                    except ValueError:
                        continue

            if next_bday < today:
                try:
                    next_bday = date(year=today.year + 1, month=b.month, day=b.day)
                except ValueError:
                    ny = today.year + 1
                    while True:
                        try:
                            next_bday = date(year=ny, month=b.month, day=b.day)
                            break
                        except ValueError:
                            ny += 1

            if today < next_bday <= end_date:
                weekday_name = uk_weekdays[next_bday.weekday()]
                result.setdefault(weekday_name, []).append((name, next_bday))

        for wd in result:
            result[wd].sort(key=lambda x: x[1])
        return result

@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        return "Error: Invalid number of arguments for 'add' command. Use: add [name] [phone]"
    name, phone = args
    book.add_contact(name, phone)
    return "Contact added."

@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 2:
        return "Error: Invalid number of arguments for 'change' command. Use: change [name] [phone]"
    name, phone = args
    book.change_contact(name, phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
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
        phone = info.get('phone', '')
        b = info.get('birthday')
        bstr = b.strftime("%d.%m.%Y") if b else "—"
        result += f"{name}: {phone} | Birthday: {bstr}\n"
    return result.strip()

@input_error
def add_birthday(args, book: AddressBook):
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
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        return "Error: Invalid number of arguments for 'show-birthday'. Use: show-birthday [name]"
    name = args[0]
    b = book.get_birthday(name)
    return b.strftime("%d.%m.%Y")

@input_error
def birthdays(args, book: AddressBook):
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
    print("Welcome to the Contact Bot (AddressBook version)!")
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
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Error: Unknown command.")

if __name__ == "__main__":
    main()