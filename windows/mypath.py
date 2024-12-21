import os
import sys

if hasattr(sys, '_MEIPASS'):
    resource_path = os.path.join(sys._MEIPASS,'resources')
else:
    resource_path = 'resources'
logo_path = os.path.join(resource_path, 'logo', 'logo.png')
background_path = os.path.join(resource_path, 'images', 'background.jpg')
warehouse_path = os.path.join(resource_path, 'icons', 'warehouse.svg')
orders_path = os.path.join(resource_path, 'icons', 'orders.svg')
project_path = os.path.join(resource_path, 'icons', 'project.svg')
provider_path = os.path.join(resource_path, 'icons', 'provider.svg')
users_path = os.path.join(resource_path, 'icons', 'users.svg')
employee_path = os.path.join(resource_path, 'icons', 'employee.svg')
file_path = os.path.join(resource_path, 'icons', 'file.svg')
logs_path = os.path.join(resource_path, 'icons', 'logs.svg')