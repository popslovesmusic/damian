import json

class InventoryManager:
    def __init__(self, contract_path, equipment_path, consumable_path, burden_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(equipment_path, 'r') as f:
            self.equipment_profile = json.load(f)
        with open(consumable_path, 'r') as f:
            self.consumable_rules = json.load(f)
        with open(burden_path, 'r') as f:
            self.burden_rules = json.load(f)
            
        self.items = {}
        self.current_burden = 0

    def add_item(self, item_id, quantity=1):
        if self.current_burden + quantity > self.burden_rules["max_burden"]:
            return False
        
        self.items[item_id] = self.items.get(item_id, 0) + quantity
        self.current_burden += quantity
        return True

    def use_item(self, item_id):
        if self.items.get(item_id, 0) > 0:
            self.items[item_id] -= 1
            self.current_burden -= 1
            return self.consumable_rules.get(item_id)
        return None
