import ifcopenshell

# ===============================
# LOAD IFC FILE
# ===============================
model = ifcopenshell.open("sample2.ifc")

print("\n================ IFC FULL ANALYSIS REPORT ================\n")
# BASIC MODEL INFO
# ===============================
all_products = model.by_type("IfcProduct")
total_elements = len(all_products)

print(f"Total IFC elements in model            : {total_elements}\n")

# ===============================
# ELEMENT-WISE CLASSIFICATION
# ===============================
walls = model.by_type("IfcWall")
standard_walls = model.by_type("IfcWallStandardCase")
doors = model.by_type("IfcDoor")
windows = model.by_type("IfcWindow")
proxies = model.by_type("IfcBuildingElementProxy")
storeys = model.by_type("IfcBuildingStorey")

total_walls = len(walls) + len(standard_walls)

# ===============================
# COUNTS
# ===============================
print("---- ELEMENT-WISE CLASSIFICATION ----")
print(f"Walls (semantic)                       : {total_walls}")
print(f"  - IfcWall                            : {len(walls)}")
print(f"  - IfcWallStandardCase                : {len(standard_walls)}")
print(f"Doors                                  : {len(doors)}")
print(f"Windows                                : {len(windows)}")
print(f"Proxy elements (non-semantic)          : {len(proxies)}")
print(f"Building storeys                       : {len(storeys)}\n")

# ===============================
# SEMANTIC VS NON-SEMANTIC METRICS
# ===============================
semantic_elements = total_walls + len(doors) + len(windows)
non_semantic_elements = len(proxies)

semantic_percentage = (semantic_elements / total_elements) * 100 if total_elements else 0
non_semantic_percentage = (non_semantic_elements / total_elements) * 100 if total_elements else 0

print("---- SEMANTIC QUALITY METRICS ----")
print(f"Semantic elements count                : {semantic_elements}")
print(f"Non-semantic (proxy) elements count    : {non_semantic_elements}")
print(f"Semantic elements percentage           : {semantic_percentage:.2f}%")
print(f"Non-semantic elements percentage       : {non_semantic_percentage:.2f}%\n")

print("---- ELEMENT-LEVEL TRACE (PROXY ELEMENTS) ----")

if len(proxies) == 0:
    print("No proxy elements detected.")
else:
    for i, proxy in enumerate(proxies, start=1):
        name = proxy.Name if proxy.Name else "Unnamed"
        global_id = proxy.GlobalId
        print(f"{i}. Proxy Element")
        print(f"   - Name      : {name}")
        print(f"   - GlobalId  : {global_id}")
        print(f"   - IFC Class : {proxy.is_a()}")
        print("   - Issue     : Semantic meaning lost (generic proxy)\n")

# ===============================
# INTERPRETATION
# ===============================
print("---- INTERPRETATION ----")

if total_walls > 0:
    print("- Wall elements retained semantic representation.")

if non_semantic_elements > 0:
    print(
        "- A significant portion of elements are represented as generic proxy objects,\n"
        "  indicating semantic degradation during IFC-based interoperability."
    )

if len(storeys) > 0:
    print("- Building levels are explicitly defined in the IFC model.")

print("\nCONCLUSION:")

if non_semantic_percentage == 0:
    print(
        "The IFC model preserves semantic representation across all analyzed elements.\n"
        "No proxy-based semantic degradation was detected, indicating high-quality\n"
        "IFC export and strong interoperability."
    )

elif non_semantic_percentage < 20:
    print(
        "The IFC model largely preserves semantic representation, with minor semantic\n"
        "degradation observed in a small portion of elements. Interoperability quality\n"
        "is generally good but not perfect."
    )

elif non_semantic_percentage < 50:
    print(
        "The IFC model exhibits mixed semantic representation. While core elements retain\n"
        "their meaning, a significant portion of components degrade into proxy elements,\n"
        "indicating moderate interoperability issues."
    )

else:
    print(
        "The IFC model shows substantial semantic degradation, with a large percentage of\n"
        "elements represented as proxy objects. This indicates poor interoperability and\n"
        "high information loss during IFC-based model exchange."
    )

print("\n================ END OF REPORT =================\n")