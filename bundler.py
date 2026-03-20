import csv
import json
import os

class PixiesBundler:
    def __init__(self, csv_path):
        self.csv_path = os.path.expanduser(csv_path)
        self.inventory = []
        self.index = {
            "rigs": {},        # Key: "Size_Gender" -> [items]
            "bangers": {},     # Key: "Size_Gender" -> [items]
            "bongs": {},       # Key: "Size_Gender" -> [items]
            "bowls": {},       # Key: "Size_Gender" -> [items]
            "batteries": {},   # Key: "Thread" -> [items]
            "carts": {},       # Key: "Thread" -> [items]
            "cleaning": [],    # List of cleaning supplies
            "torches": []      # List of torches/lighters
        }
        self.load_and_index()

    def clean_val(self, val):
        return str(val).strip()

    def load_and_index(self):
        if not os.path.exists(self.csv_path):
            print(f"Error: {self.csv_path} not found.")
            return

        with open(self.csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Status'] == 'Hidden': continue
                
                cat = row['Category'].lower()
                p_type = row['Product Type'].lower()
                size = self.clean_val(row['Size'])
                gender = self.clean_val(row['Joint Gender'])
                thread = self.clean_val(row['Thread Type'])
                key = f"{size}_{gender}"

                # Indexing Logic - Sorting by Interconnects
                if "dab rig" in cat or "dab rig" in p_type:
                    self.index["rigs"].setdefault(key, []).append(row)
                elif "banger" in p_type or "dab straw" in p_type:
                    self.index["bangers"].setdefault(key, []).append(row)
                elif "bong" in cat or "bong" in p_type:
                    self.index["bongs"].setdefault(key, []).append(row)
                elif "bowl" in p_type:
                    self.index["bowls"].setdefault(key, []).append(row)
                elif "battery" in cat:
                    self.index["batteries"].setdefault(thread, []).append(row)
                elif "cleaner" in p_type or "cleaning" in cat:
                    self.index["cleaning"].append(row)
                elif "torch" in p_type or "lighter" in cat:
                    self.index["torches"].append(row)

    def get_opposite_key(self, key):
        """Finds the mating joint (e.g., 14mm Female needs 14mm Male)."""
        if "Female" in key:
            return key.replace("Female", "Male")
        elif "Male" in key:
            return key.replace("Male", "Female")
        return key

    def build_bundles(self):
        bundles = []

        # 1. GENERATE "READY-TO-RIP" RIG SETS
        for rig_key, rig_list in self.index["rigs"].items():
            mate_key = self.get_opposite_key(rig_key)
            if mate_key in self.index["bangers"]:
                for rig in rig_list[:3]: # Limit to top 3 rigs per size
                    banger = self.index["bangers"][mate_key][0] # Take first compatible banger
                    torch = self.index["torches"][0] if self.index["torches"] else None
                    
                    bundle_data = {
                        "main_sku": rig['SKU'],
                        "bundle_name": f"Pro Dab Set: {rig['Product Name']}",
                        "items": [rig['SKU'], banger['SKU']],
                        "discount_pct": 15,
                        "description": f"Engineered set for {rig_key} rigs. Includes a precision-fit {banger['Product Name']}."
                    }
                    if torch: bundle_data["items"].append(torch["SKU"])
                    bundles.append(bundle_data)

        # 2. GENERATE "CLEAN FREAK" MAINTENANCE PACKS
        # Cross-correlates any major glass purchase with cleaning supplies
        for item_group in ["rigs", "bongs"]:
            for key in self.index[item_group]:
                for item in self.index[item_group][key][:2]:
                    if self.index["cleaning"]:
                        bundles.append({
                            "main_sku": item['SKU'],
                            "bundle_name": f"Forever Clean Pack: {item['Product Name']}",
                            "items": [item['SKU'], self.index["cleaning"][0]['SKU']],
                            "discount_pct": 10,
                            "description": "Don't let resin ruin the flavor. Bundled with industry-standard cleaner."
                        })

        return bundles

if __name__ == "__main__":
    bundler = PixiesBundler("~/Desktop/Dyspensr_Master_Catalog_Priced.csv")
    output = bundler.build_bundles()
    
    with open("bundles.json", "w") as f:
        json.dump(output, f, indent=4)
    print(f"Index complete. {len(output)} bundles cross-referenced and exported.")