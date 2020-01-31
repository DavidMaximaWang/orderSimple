from django.apps import AppConfig


class InventoryAppConfig(AppConfig):
    name = 'order_inventory_simple.apps.inventories'

    def ready(self):
        import order_inventory_simple.apps.inventories.signals


default_app_config = 'order_inventory_simple.apps.inventories.InventoryAppConfig'
