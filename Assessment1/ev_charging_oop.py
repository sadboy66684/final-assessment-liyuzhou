"""Smart Campus EV Charging System - Object-Oriented Python Implementation.
Author: Liyuzhou | Student ID: 0398565 | Module: ITS72604
OOP Features: Encapsulation, Inheritance, Composition, Polymorphism, Abstraction"""
from abc import ABC, abstractmethod
import math

class User(ABC):
    def __init__(self, user_id, name, vehicle_number):
        self.__user_id = user_id; self.__name = name; self.__vehicle_number = vehicle_number
    @property
    def user_id(self): return self.__user_id
    @user_id.setter
    def user_id(self, value):
        if value and str(value).strip(): self.__user_id = str(value).strip()
        else: raise ValueError("User ID cannot be empty.")
    @property
    def name(self): return self.__name
    @name.setter
    def name(self, value):
        if value and str(value).strip(): self.__name = str(value).strip()
        else: raise ValueError("Name cannot be empty.")
    @property
    def vehicle_number(self): return self.__vehicle_number
    @vehicle_number.setter
    def vehicle_number(self, value):
        if value and str(value).strip(): self.__vehicle_number = str(value).strip()
        else: raise ValueError("Vehicle number cannot be empty.")
    @abstractmethod
    def calculate_fee(self, gross_fee, charger_type="AC"): pass
    def __str__(self): return f"User[ID={self.__user_id}, Name={self.__name}, Vehicle={self.__vehicle_number}]"
    def __repr__(self): return f"User(user_id='{self.__user_id}', name='{self.__name}', vehicle_number='{self.__vehicle_number}')"
    def __eq__(self, other):
        if not isinstance(other, User): return False
        return self.__user_id == other.__user_id

class MemberUser(User):
    VALID_MEMBER_TYPES = ["FIRST-TIME", "STAFF", "STUDENT", "REGULAR"]
    def __init__(self, user_id, name, vehicle_number, member_type, has_eco_pass=False):
        super().__init__(user_id, name, vehicle_number)
        self.__member_type = member_type; self.__has_eco_pass = has_eco_pass
    @property
    def member_type(self): return self.__member_type
    @member_type.setter
    def member_type(self, value):
        value = str(value).upper()
        if value in self.VALID_MEMBER_TYPES: self.__member_type = value
        else: raise ValueError(f"Invalid member type. Must be one of: {self.VALID_MEMBER_TYPES}")
    @property
    def has_eco_pass(self): return self.__has_eco_pass
    @has_eco_pass.setter
    def has_eco_pass(self, value): self.__has_eco_pass = bool(value)
    @classmethod
    def from_string(cls, user_string):
        parts = user_string.split("|")
        if len(parts) != 5: raise ValueError("String must have 5 parts separated by '|'")
        user_id, name, vehicle_number, member_type, eco_pass = parts
        return cls(user_id, name, vehicle_number, member_type, eco_pass == "True")
    def calculate_fee(self, gross_fee, charger_type="AC"):
        if self.__member_type == "FIRST-TIME": return gross_fee
        elif self.__member_type == "STAFF": return gross_fee * 0.50
        elif self.__member_type == "STUDENT" and charger_type == "AC": return gross_fee * 0.25
        return 0.00
    def get_eco_discount(self): return 2.00 if self.__has_eco_pass else 0.00
    def __str__(self):
        eco = "Yes" if self.__has_eco_pass else "No"
        return f"MemberUser[ID={self.user_id}, Name={self.name}, Vehicle={self.vehicle_number}, Type={self.__member_type}, EcoPass={eco}]"
    def __repr__(self):
        return f"MemberUser(user_id='{self.user_id}', name='{self.name}', vehicle_number='{self.vehicle_number}', member_type='{self.__member_type}', has_eco_pass={self.__has_eco_pass})"
    def __eq__(self, other):
        if not isinstance(other, MemberUser): return False
        return self.user_id == other.user_id

class EVCharger:
    SUPPORTED_TYPES = ["AC", "DC"]
    def __init__(self, charger_id, charger_type, location):
        self.__charger_id = charger_id; self.__charger_type = charger_type.upper()
        self.__location = location; self.__is_occupied = False
    @property
    def charger_id(self): return self.__charger_id
    @charger_id.setter
    def charger_id(self, value):
        if value and str(value).strip(): self.__charger_id = str(value).strip()
    @property
    def charger_type(self): return self.__charger_type
    @charger_type.setter
    def charger_type(self, value):
        value = str(value).upper()
        if value in self.SUPPORTED_TYPES: self.__charger_type = value
        else: raise ValueError(f"Charger type must be one of: {self.SUPPORTED_TYPES}")
    @property
    def location(self): return self.__location
    @location.setter
    def location(self, value): self.__location = value
    @property
    def is_occupied(self): return self.__is_occupied
    def set_occupied(self, status): self.__is_occupied = bool(status)
    @staticmethod
    def is_valid_charger_type(charger_type): return str(charger_type).upper() in EVCharger.SUPPORTED_TYPES
    @classmethod
    def get_supported_types(cls): return cls.SUPPORTED_TYPES.copy()
    def get_hourly_rate(self, rounded_hours):
        if self.__charger_type == "AC":
            if 1 <= rounded_hours <= 2: return 4.00
            elif 3 <= rounded_hours <= 4: return 6.00
            elif 5 <= rounded_hours <= 6: return 8.00
            else: return 12.00
        else:
            if 1 <= rounded_hours <= 2: return 10.00
            elif 3 <= rounded_hours <= 4: return 15.00
            elif 5 <= rounded_hours <= 6: return 20.00
            else: return 30.00
    def get_overtime_cap(self): return 80.00 if self.__charger_type == "AC" else 150.00
    def __str__(self):
        status = "Occupied" if self.__is_occupied else "Available"
        kw = "7kW AC" if self.__charger_type == "AC" else "50kW DC"
        return f"EVCharger[ID={self.__charger_id}, Type={kw}, Location={self.__location}, Status={status}]"
    def __eq__(self, other):
        if not isinstance(other, EVCharger): return False
        return self.__charger_id == other.__charger_id

class ChargingSession:
    def __init__(self, session_id, user, charger, hours_charged, is_peak_hour=False, is_idle_parking=False, is_lost_card=False):
        self.__session_id = session_id; self.__user = user; self.__charger = charger
        self.__hours_charged = hours_charged; self.__is_peak_hour = is_peak_hour
        self.__is_idle_parking = is_idle_parking; self.__is_lost_card = is_lost_card
        self.__rounded_hours = math.ceil(hours_charged)
    @property
    def session_id(self): return self.__session_id
    @property
    def user(self): return self.__user
    @property
    def charger(self): return self.__charger
    @property
    def hours_charged(self): return self.__hours_charged
    @property
    def rounded_hours(self): return self.__rounded_hours
    @staticmethod
    def validate_hours(hours):
        try: return float(hours) > 0
        except (ValueError, TypeError): return False
    def calculate_gross_fee(self):
        rate = self.__charger.get_hourly_rate(self.__rounded_hours)
        gross_fee = rate * self.__rounded_hours
        if self.__rounded_hours > 6: gross_fee = min(gross_fee, self.__charger.get_overtime_cap())
        return gross_fee, rate
    def calculate_surcharges(self):
        sa = 0.00; sd = []
        if self.__is_peak_hour: sa += 5.00; sd.append("Peak Hour Surcharge: RM 5.00")
        if self.__is_idle_parking: sa += 15.00; sd.append("Idle Parking Surcharge: RM 15.00")
        if self.__is_lost_card: sa += 30.00; sd.append("Lost RFID Card Replacement: RM 30.00")
        return sa, sd
    def calculate_net_payable(self):
        gross_fee, rate = self.calculate_gross_fee()
        discount_amount = self.__user.calculate_fee(gross_fee, self.__charger.charger_type)
        eco_discount = self.__user.get_eco_discount() if isinstance(self.__user, MemberUser) else 0.00
        sa, sd = self.calculate_surcharges()
        total_discount = discount_amount + eco_discount
        fee_after_discount = max(gross_fee - total_discount, 0.00)
        net_payable = fee_after_discount + sa
        return {"gross_fee": gross_fee, "rate": rate, "discount_amount": discount_amount, "eco_discount": eco_discount, "total_discount": total_discount, "surcharge_amount": sa, "surcharge_details": sd, "fee_after_discount": fee_after_discount, "net_payable": net_payable}
    def generate_bill(self):
        r = self.calculate_net_payable()
        mt = self.__user.member_type if isinstance(self.__user, MemberUser) else ""
        print("\n" + "=" * 60)
        print("   TAYLOR'S UNIVERSITY SMART CAMPUS EV CHARGING")
        print("         OFFICIAL PARKING BILL (OOP VERSION)")
        print("=" * 60)
        print(f"  Session ID      : {self.__session_id}")
        print(f"  User ID         : {self.__user.user_id}")
        print(f"  User Name       : {self.__user.name}")
        print(f"  Vehicle Number  : {self.__user.vehicle_number}")
        if mt: print(f"  Member Type     : {mt}")
        ct = self.__charger.charger_type
        print(f"  Charger ID      : {self.__charger.charger_id}")
        print(f"  Charger Type    : {ct} ({'7kW AC' if ct == 'AC' else '50kW DC'})")
        print(f"  Charger Location: {self.__charger.location}")
        print(f"  Hours Charged   : {self.__hours_charged:.1f} hrs (rounded to {self.__rounded_hours} hrs)")
        print("-" * 60)
        print("  CHARGING FEE BREAKDOWN:")
        print(f"    Hourly Rate        : RM {r['rate']:.2f}/hr")
        print(f"    Rounded Hours      : {self.__rounded_hours} hour(s)")
        print(f"    Gross Charging Fee : RM {r['gross_fee']:.2f}")
        print("-" * 60)
        print("  DISCOUNTS & WAIVERS:")
        if r['discount_amount'] > 0 and isinstance(self.__user, MemberUser):
            labels = {"FIRST-TIME": "First-Time User Waiver (100%)", "STAFF": "Staff Member Discount (50%)", "STUDENT": "Student Discount (25%)"}
            print(f"    {labels.get(self.__user.member_type, 'Member Discount'):<35} - RM {r['discount_amount']:.2f}")
        else: print(f"    Member Discount{'':<26} - None")
        if r['eco_discount'] > 0: print(f"    Green Eco-Pass Discount{'':<18} - RM {r['eco_discount']:.2f}")
        else: print(f"    Green Eco-Pass Discount{'':<18} - Not Applicable")
        print(f"    Total Discount{'':<26} - RM {r['total_discount']:.2f}")
        print("-" * 60)
        print("  SURCHARGES:")
        if r['surcharge_details']:
            for d in r['surcharge_details']: print(f"    {d}")
        else: print("    None")
        print(f"    Total Surcharges{'':<23} + RM {r['surcharge_amount']:.2f}")
        print("=" * 60)
        print(f"  Fee After Discounts : RM {r['fee_after_discount']:.2f}")
        print(f"  Net Amount Payable  : RM {r['net_payable']:.2f}")
        print("=" * 60 + "\n")
    def __str__(self):
        return f"ChargingSession[ID={self.__session_id}, User={self.__user.user_id}, Charger={self.__charger.charger_id}, Hours={self.__hours_charged}]"
    def __eq__(self, other):
        if not isinstance(other, ChargingSession): return False
        return self.__session_id == other.__session_id

def main():
    print("\n" + "*" * 60)
    print("  TAYLOR'S UNIVERSITY SMART CAMPUS EV CHARGING (OOP)")
    print("*" * 60)
    charger_ac = EVCharger("AC-01", "AC", "Block A - Lot 12")
    charger_dc = EVCharger("DC-01", "DC", "Block C - Lot 5")
    charger_ac2 = EVCharger("AC-02", "AC", "Block B - Lot 8")
    print("\n  Available Chargers:")
    print(f"    {charger_ac}\n    {charger_dc}\n    {charger_ac2}")
    print(f"\n  Static: EVCharger.is_valid_charger_type('AC') = {EVCharger.is_valid_charger_type('AC')}")
    print(f"  Class:  EVCharger.get_supported_types() = {EVCharger.get_supported_types()}")
    # Scenario 1: Staff + DC + Peak Hour + Eco-Pass
    print("\n" + "=" * 60 + "\n  SCENARIO 1: Staff - DC - Peak Hour\n" + "=" * 60)
    staff = MemberUser("0398565", "Liyuzhou", "ABC1234", "STAFF", True)
    print(f"  Created: {staff}")
    charger_dc.set_occupied(True)
    ChargingSession("S-1001", staff, charger_dc, 4.5, True, False, False).generate_bill()
    # Scenario 2: First-Time + AC + 100% Waiver
    print("=" * 60 + "\n  SCENARIO 2: First-Time - AC - Full Waiver\n" + "=" * 60)
    first = MemberUser("STU001", "Alice Tan", "XYZ9999", "FIRST-TIME", False)
    print(f"  Created: {first}")
    charger_ac.set_occupied(True)
    ChargingSession("S-1002", first, charger_ac, 2.0, False, False, False).generate_bill()
    # Scenario 3: Student + AC + Idle + Lost Card
    print("=" * 60 + "\n  SCENARIO 3: Student - AC - Idle + Lost Card\n" + "=" * 60)
    student = MemberUser("STU002", "Bob Lim", "DEF5678", "STUDENT", True)
    print(f"  Created: {student}")
    charger_ac2.set_occupied(True)
    ChargingSession("S-1003", student, charger_ac2, 5.2, False, True, True).generate_bill()
    # Scenario 4: Regular + DC + Overtime
    print("=" * 60 + "\n  SCENARIO 4: Regular - DC - Overtime\n" + "=" * 60)
    regular = MemberUser("VIS001", "Charlie Wong", "GHI9012", "REGULAR", False)
    print(f"  Created: {regular}")
    charger_dc.set_occupied(True)
    ChargingSession("S-1004", regular, charger_dc, 8.0, False, False, False).generate_bill()
    # Polymorphism demo
    print("\n" + "=" * 60 + "\n  POLYMORPHISM: calculate_fee() on gross RM 100.00\n" + "=" * 60)
    for u in [MemberUser("M001", "Staff", "V002", "STAFF"), MemberUser("M002", "Student", "V003", "STUDENT"), MemberUser("M003", "First-Time", "V004", "FIRST-TIME"), MemberUser("M004", "Regular", "V005", "REGULAR")]:
        print(f"    {type(u).__name__:>12}.calculate_fee(100.00) = RM {u.calculate_fee(100.00):.2f}  <- {u}")
    # Class method demo
    print("\n" + "=" * 60 + "\n  CLASS METHOD: MemberUser.from_string()\n" + "=" * 60)
    mu = MemberUser.from_string("TEST01|Test User|WXYZ001|STUDENT|True")
    print(f"    Created: {mu}")
    # Validation demo
    print("\n" + "=" * 60 + "\n  ENCAPSULATION / VALIDATION\n" + "=" * 60)
    try: mu.member_type = "INVALID"
    except ValueError as e: print(f"    Error: {e}")
    try: mu.user_id = ""
    except ValueError as e: print(f"    Error: {e}")
    print("\n" + "*" * 60 + "\n  All scenarios completed!\n" + "*" * 60)

if __name__ == "__main__":
    main()