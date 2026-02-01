from collections import UserDict
from datetime import date, datetime, timedelta

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
        if not (value.isdigit() and len(value) ==10):
            raise ValueError("Phone number must be exactly 10 digits and contain only numbers")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)
        
    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
            return True
        return False

    
    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if phone:
            Phone(new_number)
            phone.value = new_number
            return True
        raise ValueError("Old phone number not found")

    
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone 
        return None 
    
    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)
    
    def __str__(self):
        if self.birthday:
            return f"Contact(Name: {self.name}, Phones: {[str(phone) for phone in self.phones]}, Birthday: {self.birthday})"
        return f"Contact(Name: {self.name}, Phones: {[str(phone) for phone in self.phones]})"
    
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        
    def find(self, name):
        return self.data.get(name, None)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False
    
    def get_upcoming_birthdays(self):
        today = date.today()
        end = today + timedelta(days=7)
        result = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bd = record.birthday.value
            try_year = today.year
            next_birthday = bd.replace(year=try_year)
            if next_birthday < today:
                next_birthday = bd.replace(year=try_year + 1)
            if today <= next_birthday.date() <= end:
                greeting = next_birthday
                if greeting.weekday() == 5:
                    greeting += timedelta(days=2)
                elif greeting.weekday() == 6:
                    greeting += timedelta(days=1)
                result.append({"name": record.name.value, "birthday": greeting.strftime("%d.%m.%Y")})
        return result
        
            
        

    
    def __str__(self):
        return '\n'.join([str(record) for record in self.data.values()])
    
if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    print(book)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: John: 5555555555

    # Видалення запису Jane
    book.delete("Jane")
    

        
        
    