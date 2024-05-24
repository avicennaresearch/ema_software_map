import json
import argparse
from functools import cmp_to_key

FILE_NAME = "EMA_Feature_Comparison.json"

def _add_package(d, pkg_name, is_feature=True):
    def _custom_cmpr(item1, item2):
        i1 = item1[0].lower()
        i2 = item2[0].lower()
        i1_tkns = [x.strip() for x in i1.split("-")]
        i1_pkg = i1_tkns[0]
        i1_purpose = i1_tkns[1]
        i2_tkns = [x.strip() for x in i2.split("-")]
        i2_pkg = i2_tkns[0]
        i2_purpose = i2_tkns[1]
        if i1_pkg > i2_pkg:
            return 1
        if i1_pkg < i2_pkg:
            return -1
        if i1_purpose == "Score":
            return -1
        return 1

    key_function = cmp_to_key(_custom_cmpr)
    org_items = list(d.items())
    final_items = [
        org_items[0], # Row ID
        org_items[1] # Feature Name
    ]
    if is_feature:
        org_items.append((f"{pkg_name} - Score", ""))
        org_items.append((f"{pkg_name} - Notes", ""))
        sorted_list = sorted(org_items[2:], key=key_function)
        final_items.extend(sorted_list)
    else:
        org_items.insert(-1, (f"{pkg_name} - Score", ""))
        org_items.insert(-1, (f"{pkg_name} - Notes", ""))
        sorted_list = sorted(org_items[2:-1], key=key_function)
        final_items.extend(sorted_list)
        final_items.append(org_items[-1])
    return dict(final_items)

def main():
    parser = argparse.ArgumentParser(description="Process some strings.")
    parser.add_argument('pkg_name', type=str, help='Package name')

    args = parser.parse_args()

    data = None

    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    for ic in range(len(data["categories"])):
        cat = data["categories"][ic]
        for isc in range(len(cat["subcategories"])):
            subcat = cat["subcategories"][isc]
            for ift in range(len(subcat["features"])):
                feature = subcat["features"][ift]
                subcat["features"][ift] = _add_package(
                    feature, args.pkg_name, False
                )
            cat["subcategories"][isc] = _add_package(
                subcat, args.pkg_name, False
            )
        data["categories"][ic] = _add_package(cat, args.pkg_name, False)

    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()