# Copyright (c) 2026 Ahmet Ardıl Çiftçi. All rights reserved.
# Developed by Ahmet Ardıl Çiftçi - Sales Decision Support System (SDSS)

import random
import sys
import ollama  # Ollama library used to connect to the local LLM model.

# ==============================================================================
# COMPANY / MANAGEMENT CONFIGURATION
# ==============================================================================
SHOW_ADVISOR_COACHING = True

# 💳 CAMPAIGN PARAMETERS (Configurable)
# Set CAMPAIGN_ACTIVE = False when the campaign period ends.
CAMPAIGN_ACTIVE = True 
CAMPAIGN_INSTALLMENTS = 9
CAMPAIGN_CARDS = "Yapı Kredi World & İş Bankası Maximum"
STANDARD_INSTALLMENTS = 6  # Standard installment duration updated to 6 months.

# ==============================================================================
# ARTICLE DATABASE
# ==============================================================================
ARTICLE_DATABASE = {
    "1615257": {
        "article_no": "1615257",
        "name": "Lenovo IdeaPad Slim 3, Daily / Office Laptop - Entry",
        "category": "Computer",
        "product_group": "NB",
        "color": "Grey",
        "price": 26999.00,
        "features": "AMD Ryzen 5 40/ 8GB RAM / 512GB SSD / 15.6 FHD/W11/82XQ0112TX",
        "warehouse_6_stock": 14,
        "availability": True
    },
    "1615267": {
        "article_no": "1615267",
        "name": "Lenovo Yoga Slim 7 Aura Edition, Daily / Office Laptop - Mid-Range",
        "category": "Computer",
        "product_group": "NB",
        "color": "Silver",
        "price": 57999.00,
        "features": "Intel Core Ultra 5 226V/ 16GB RAM / 512GB SSD / 14 OLED/W11/83JX00BATR",
        "warehouse_6_stock": 15,
        "availability": True
    },
    "1615277": {
        "article_no": "1615277",
        "name": "Lenovo Yoga 7 2-in-1, Daily / Office Laptop - Business VIP",
        "category": "Computer",
        "product_group": "NB",
        "color": "Space Grey",
        "price": 79999.00,
        "features": "AMD Ryzen AI 7 350/ 16GB RAM / 1TB SSD /14 OLED/W11/83JR00AETR",
        "warehouse_6_stock": 6,
        "availability": True
    }
}

SERVICE_DATABASE = {
    "OFFICE_LIFETIME": {"name": "Microsoft Office Lifetime", "price": 7999.00},
    "OFFICE_365": {"name": "Microsoft 365 Annual Subscription", "price": 2599.00},
    "MAINTENANCE_COMBI": {"name": "Boiler & Radiator Maintenance Package", "price": 4299.00},
    "MAINTENANCE_IRON": {"name": "Iron / Small Appliance Maintenance Package", "price": 2099.00},
    "ANTIVIRUS_1YR": {"name": "1-Year Premium Antivirus Protection", "price": 1299.00}
}


def generate_pitch_sentence_llm(profile_color, product_name, daily_cost):
    # Convert daily amount to monthly cost (based on 30 days)
    monthly_cost = daily_cost * 30

    system_prompt = (
        "You are an expert sales consultant working at a retail electronics store. "
        "You MUST speak strictly in English. "
        "Your goal is to construct a SINGLE, natural, and persuasive sales pitch sentence "
        "that convinces the customer to buy extended warranty/extra packages. "
        "Output ONLY the pitch sentence inside quotation marks. Do not say hello or add explanations."
    )

    user_prompt = (
        f"Product: {product_name}\n"
        f"Customer Profile: {profile_color}\n"  
        f"Monthly Additional Cost: ${monthly_cost:,.2f}\n\n"
        f"Give me a single, natural, and fluent English sales pitch sentence that emphasizes the importance "
        f"of getting a warranty/extra package with a monthly cost of ${monthly_cost:,.2f}."
    )

    try:
        response = ollama.chat(
            model='qwen2.5:3b',  # The target LLM model
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            options={
                'temperature': 0.2  # Low temperature ensures concise and focused output
            }
        )
        return response['message']['content'].strip()
        
    except Exception as e:
        # Fallback pitch sentence if an issue occurs
        return f"\"Sir/Madam, we can fully secure your {product_name} for an additional cost of only ${monthly_cost:,.2f} per month.\""

    
# 🔄 ALTERNATIVE DEVICE SUGGESTION ALGORITHM 
def find_alternative_devices(current_article):
    current_item = ARTICLE_DATABASE[current_article]
    curr_price = current_item["price"]
    curr_cat = current_item["category"]
    
    alternatives = []
    
    for art_no, item in ARTICLE_DATABASE.items():
        if art_no == current_article:
            continue
        if item["category"] == curr_cat:
            price_diff = item["price"] - curr_price
            alternatives.append({
                "article_no": art_no,
                "name": item["name"],
                "price": item["price"],
                "diff": price_diff,
                "stock": item["warehouse_6_stock"]
            })
            
    return alternatives


def get_segment_and_coaching(price, show_coaching=SHOW_ADVISOR_COACHING):
    if price <= 43000:
        segment_name = "LOW_SEGMENT ($0 - $43,000)"
        profile_color = "BLUE"
        coaching = {
            "risk_index": "⚠️ 85% CHURN RISK (Customer may avoid high warranty costs!)",
            "target": "🎯 Primary Target: Ensure receipt is NOT EMPTY of protection services.",
            "recommendation": "Recommend 1-Year Budget Warranty + Antivirus/Maintenance Package instead of full coverage.",
            "customer_profile": "🟢 Blue Profile (High Price Sensitivity / Analytical)"
        }
    elif 44000 <= price <= 68000:
        segment_name = "MID_SEGMENT ($44,000 - $68,000)"
        profile_color = "YELLOW"
        coaching = {
            "risk_index": "⚖️ 40% MEDIUM RISK (Balanced Persuasion Stage)",
            "target": "🎯 Primary Target: Complete bundle closure with a Mid/High Budget Package.",
            "recommendation": "Pitch 2-Year Warranty + Office. Pivot to 1-Year Warranty immediately if the customer hesitates.",
            "customer_profile": "🟡 Yellow Profile (Value / Cost Balanced)"
        }
    else:
        segment_name = "HIGH_SEGMENT / VIP ($68,000 and Above)"
        profile_color = "GREEN"
        coaching = {
            "risk_index": "🎯 10% CHURN RISK (95% Service / Warranty Closure Opportunity)",
            "target": "🎯 Primary Target: Receipt MUST CLOSE with at least 2-Year VIP Warranty.",
            "recommendation": "Emphasize high physical risk of device. Anchor with VIP Protection + Maintenance + Lifetime Office package.",
            "customer_profile": "🟣 Green Profile (Maximum Risk Sensitivity / Trust Oriented)"
        }

    return segment_name, profile_color, (coaching if show_coaching else None)


def generate_offer(article_no):
    if article_no not in ARTICLE_DATABASE:
        print("\n❌ ERROR: Entered Article Number Not Found in Database!\n")
        return

    item = ARTICLE_DATABASE[article_no]
    price = item["price"]
    
    segment_name, profile_color, coaching = get_segment_and_coaching(price)

    # Warranty Calculation
    warranty_1_yr = price * 0.12
    warranty_2_yr = price * 0.22

    if price <= 43000:
        recommended_service = SERVICE_DATABASE["ANTIVIRUS_1YR"]
        recommended_maintenance = SERVICE_DATABASE["MAINTENANCE_IRON"]
        warranty_selection = warranty_1_yr
        warranty_name = "1-Year Standard Insurance"
    elif 44000 <= price <= 68000:
        recommended_service = SERVICE_DATABASE["OFFICE_365"]
        recommended_maintenance = SERVICE_DATABASE["MAINTENANCE_COMBI"]
        warranty_selection = warranty_2_yr
        warranty_name = "2-Year Extended Warranty"
    else:
        recommended_service = SERVICE_DATABASE["OFFICE_LIFETIME"]
        recommended_maintenance = SERVICE_DATABASE["MAINTENANCE_COMBI"]
        warranty_selection = warranty_2_yr
        warranty_name = "2+2 Year VIP Warranty"

    extra_services_total = warranty_selection + recommended_service["price"] + recommended_maintenance["price"]
    cart_without_discount = price + extra_services_total

    discount_amount = price * 0.10
    net_device_price = price - discount_amount
    cart_with_discount = net_device_price + extra_services_total

    installment_count = CAMPAIGN_INSTALLMENTS if CAMPAIGN_ACTIVE else STANDARD_INSTALLMENTS

    monthly_without_discount = cart_without_discount / installment_count
    daily_without_discount = monthly_without_discount / 30.0

    monthly_with_discount = cart_with_discount / installment_count
    daily_with_discount = monthly_with_discount / 30.0

    # Generate Real-Time Persuasion Sentence
    pitch_sentence = generate_pitch_sentence_llm(profile_color, item['name'], daily_without_discount)

    # ==========================================================================
    # OUTPUT SCREEN
    # ==========================================================================
    print("\n" + "=" * 75)
    print(f" 🛒 RETAIL SALES DECISION SUPPORT SYSTEM (SDSS)")
    print("=" * 75)
    print(f"ARTICLE NO  : {item['article_no']} | CATEGORY: {item['category']} ({item['product_group']})")
    print(f"PRODUCT NAME: {item['name']} [{item['color']}]")
    print(f"FEATURES    : {item['features']}")
    print(f"BASE PRICE  : ${price:,.2f}")
    print("-" * 75)

    print("📌 OPERATIONAL STOCK INFORMATION:")
    if item['warehouse_6_stock'] > 0:
        print(f"  📦 Warehouse 6 (Sealed Box) : {item['warehouse_6_stock']} UNITS [READY FOR SALE]")
    else:
        print(f"  ⚠️ Warehouse 6 (Sealed Box) : 0 UNITS [SEALED BOX STOCK OUT!]")

    print(f"  🖥️ Display Status          : {'In Display' if item['availability'] else 'Not in Display'}")

    print("-" * 75)
    print(f"📊 CUSTOMER SEGMENT: {segment_name}")

    if coaching:
        print("\n💡 ADVISOR COACHING & WARRANTY RISK INDEX:")
        print(f"  • Risk Index   : {coaching['risk_index']}")
        print(f"  • Sales Target : {coaching['target']}")
        print(f"  • Customer Type: {coaching['customer_profile']}")

    print("\n🗣️ RECOMMENDED LIVE PERSUASION PITCH:")
    print(f"  👉 {pitch_sentence}")

    print("-" * 75)
    print("📋 RECOMMENDED BUNDLED PACKAGE CONTENT:")
    print(f"  • {warranty_name:<32}: ${warranty_selection:,.2f}")
    print(f"  • {recommended_service['name']:<32}: ${recommended_service['price']:,.2f}")
    print(f"  • {recommended_maintenance['name']:<32}: ${recommended_maintenance['price']:,.2f}")
    print(f"  👉 Total Additional Services/Insurance : ${extra_services_total:,.2f}")
    print("-" * 75)

    if CAMPAIGN_ACTIVE:
        print(f"💳 ACTIVE INSTALLMENT CAMPAIGN: {CAMPAIGN_INSTALLMENTS} Installments at Cash Price")
        print(f"   (Eligible Cards: {CAMPAIGN_CARDS})")
    else:
        print(f"💳 STANDARD PAYMENT PLAN: {STANDARD_INSTALLMENTS} Installments")

    print("\n🔍 DISCOUNT COMPARISON TABLE (CODE 10):")
    print(f" {'Metric':<28} | {'STANDARD (No Discount)':<20} | {'SPECIAL DISCOUNT (10%)':<20}")
    print(" " + "-" * 73)
    print(f" {'Device Price':<28} | ${price:,.2f}{'':<9} | ${net_device_price:,.2f}")
    print(f" {'Total Cart Value':<28} | ${cart_without_discount:,.2f}{'':<9} | ${cart_with_discount:,.2f}")
    print(f" {'Monthly (' + str(installment_count) + ' Mos)':<28} | ${monthly_without_discount:,.2f}/mo{'':<6} | ${monthly_with_discount:,.2f}/mo")
    print(f" {'🔥 DAILY COST':<28} | ${daily_without_discount:,.2f}/day{'':<6} | ${daily_with_discount:,.2f}/day")

    # Show Alternative Devices
    alternatives = find_alternative_devices(article_no)
    if alternatives:
        print("-" * 75)
        print("🔄 ALTERNATIVE DEVICE SUGGESTIONS: ")
        for alt in alternatives:
            direction = "Higher Segment" if alt["diff"] > 0 else "Budget Friendly"
            print(f"  • [{direction}] {alt['name']} | Price: ${alt['price']:,.2f} (Diff: ${alt['diff']:+,.2f}) | Stock: {alt['stock']} Units")
    
    print("=" * 75 + "\n")


def main():
    print("\n Retail Sales Decision Support System Starting...")
    while True:
        print("\n--- ARTICLE QUERY ---")
        article_input = input("Please Enter Article Number (Type 'q' to quit): ").strip()

        if article_input.lower() == 'q':
            print("Exiting system. Have a great shift!")
            break

        if not article_input:
            continue

        generate_offer(article_input)

if __name__ == "__main__":
    main()
