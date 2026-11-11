"""Smart Campus EV Charging System - Procedural Python Implementation.
Author: Liyuzhou | Student ID: 0398565 | Module: ITS72604"""
import math

AC_RATE_TIER1, AC_RATE_TIER2, AC_RATE_TIER3, AC_RATE_TIER4 = 4.00, 6.00, 8.00, 12.00
AC_MAX_FEE = 80.00
DC_RATE_TIER1, DC_RATE_TIER2, DC_RATE_TIER3, DC_RATE_TIER4 = 10.00, 15.00, 20.00, 30.00
DC_MAX_FEE = 150.00
ECO_PASS_DISCOUNT, PEAK_HOUR_SURCHARGE, IDLE_PARKING_SURCHARGE, LOST_CARD_FEE = 2.00, 5.00, 15.00, 30.00

def get_hourly_rate(charger_type, hours_charged):
    rounded_hours = math.ceil(hours_charged)
    if charger_type == "AC":
        if 1 <= rounded_hours <= 2: rate = AC_RATE_TIER1
        elif 3 <= rounded_hours <= 4: rate = AC_RATE_TIER2
        elif 5 <= rounded_hours <= 6: rate = AC_RATE_TIER3
        else: rate = AC_RATE_TIER4
    elif charger_type == "DC":
        if 1 <= rounded_hours <= 2: rate = DC_RATE_TIER1
        elif 3 <= rounded_hours <= 4: rate = DC_RATE_TIER2
        elif 5 <= rounded_hours <= 6: rate = DC_RATE_TIER3
        else: rate = DC_RATE_TIER4
    else: rate = 0.00
    return rate, rounded_hours

def calculate_gross_fee(charger_type, hours_charged):
    rate, rounded_hours = get_hourly_rate(charger_type, hours_charged)
    gross_fee = rate * rounded_hours
    if charger_type == "AC" and rounded_hours > 6: gross_fee = min(gross_fee, AC_MAX_FEE)
    elif charger_type == "DC" and rounded_hours > 6: gross_fee = min(gross_fee, DC_MAX_FEE)
    return gross_fee, rate, rounded_hours

def apply_member_discount(gross_fee, member_type, charger_type):
    discount_amount = 0.00; discount_description = "None"
    if member_type == "FIRST-TIME": discount_amount = gross_fee; discount_description = "First-Time User Waiver (100%)"
    elif member_type == "STAFF": discount_amount = gross_fee * 0.50; discount_description = "Taylor's Staff Member Discount (50%)"
    elif member_type == "STUDENT" and charger_type == "AC": discount_amount = gross_fee * 0.25; discount_description = "Taylor's Student Member Discount (25%)"
    elif member_type == "STUDENT" and charger_type == "DC": discount_amount = 0.00; discount_description = "None (Student discount: AC only)"
    return discount_amount, discount_description

def calculate_surcharges(is_peak_hour, is_idle_parking, is_lost_card):
    surcharge_amount = 0.00; surcharge_details = []
    if is_peak_hour: surcharge_amount += PEAK_HOUR_SURCHARGE; surcharge_details.append("Peak Hour Surcharge: RM 5.00")
    if is_idle_parking: surcharge_amount += IDLE_PARKING_SURCHARGE; surcharge_details.append("Idle Parking Surcharge: RM 15.00")
    if is_lost_card: surcharge_amount += LOST_CARD_FEE; surcharge_details.append("Lost RFID Card Replacement: RM 30.00")
    return surcharge_amount, surcharge_details

def display_bill(user_id, vehicle_number, member_type, charger_type, hours_charged, rate, rounded_hours, gross_fee, discount_amount, discount_description, eco_pass_discount, surcharge_amount, surcharge_details, net_payable):
    print("\n" + "=" * 60)
    print("   TAYLOR'S UNIVERSITY SMART CAMPUS EV CHARGING")
    print("              OFFICIAL PARKING BILL")
    print("=" * 60)
    print(f"  User ID         : {user_id}")
    print(f"  Vehicle Number  : {vehicle_number}")
    print(f"  Member Type     : {member_type}")
    print(f"  Charger Type    : {charger_type} ({'7kW AC' if charger_type == 'AC' else '50kW DC'})")
    print(f"  Hours Charged   : {hours_charged:.1f} hrs (rounded to {rounded_hours} hrs)")
    print("-" * 60)
    print("  CHARGING FEE BREAKDOWN:")
    print(f"    Hourly Rate        : RM {rate:.2f}/hr")
    print(f"    Rounded Hours      : {rounded_hours} hour(s)")
    print(f"    Gross Charging Fee : RM {gross_fee:.2f}")
    print("-" * 60)
    print("  DISCOUNTS & WAIVERS:")
    print(f"    {discount_description:<35} - RM {discount_amount:.2f}")
    if eco_pass_discount > 0: print(f"    Green Eco-Pass Discount{'':<16} - RM {eco_pass_discount:.2f}")
    else: print(f"    Green Eco-Pass Discount{'':<16} - Not Applicable")
    total_discount = discount_amount + eco_pass_discount
    print(f"    Total Discount{'':<26} - RM {total_discount:.2f}")
    print("-" * 60)
    print("  SURCHARGES:")
    if surcharge_details:
        for detail in surcharge_details: print(f"    {detail}")
    else: print("    None")
    print(f"    Total Surcharges{'':<23} + RM {surcharge_amount:.2f}")
    print("=" * 60)
    fee_after_discount = gross_fee - total_discount
    print(f"  Fee After Discounts : RM {fee_after_discount:.2f}")
    print(f"  Net Amount Payable  : RM {net_payable:.2f}")
    print("=" * 60 + "\n")

def run_session(user_id, vehicle_number, member_type, charger_type, hours_charged, is_peak_hour, is_idle_parking, is_lost_card, has_eco_pass):
    gross_fee, rate, rounded_hours = calculate_gross_fee(charger_type, hours_charged)
    discount_amount, discount_description = apply_member_discount(gross_fee, member_type, charger_type)
    eco_pass_discount = ECO_PASS_DISCOUNT if has_eco_pass else 0.00
    surcharge_amount, surcharge_details = calculate_surcharges(is_peak_hour, is_idle_parking, is_lost_card)
    total_discount = discount_amount + eco_pass_discount
    fee_after_discount = max(gross_fee - total_discount, 0.00)
    net_payable = fee_after_discount + surcharge_amount
    display_bill(user_id, vehicle_number, member_type, charger_type, hours_charged, rate, rounded_hours, gross_fee, discount_amount, discount_description, eco_pass_discount, surcharge_amount, surcharge_details, net_payable)

def main():
    print("\n" + "*" * 60)
    print("  TAYLOR'S UNIVERSITY SMART CAMPUS EV CHARGING & PARKING SYSTEM")
    print("*" * 60)
    print("\n  --- Session #1 ---")
    run_session("0398565", "ABC1234", "STAFF", "AC", 3.5, True, False, False, True)
    print("\n  --- Session #2 ---")
    run_session("STU002", "DEF5678", "STUDENT", "DC", 4.0, False, True, False, False)
    print("\n  --- Session #3 ---")
    run_session("NEW001", "NEW1111", "FIRST-TIME", "AC", 2.5, False, False, False, False)

if __name__ == "__main__":
    main()