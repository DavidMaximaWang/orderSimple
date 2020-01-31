## Installation

1. Clone this repository: using `git clone`.
2. `cd` into project root dir.
3. Create a new virtualenv called `env`: `virtualenv env`.
4. Active virtualenv:: `source env/bin/activate`.
5. Install requirements by: `pip install -r requirements.txt`.
6. Create db: using `python manage.py makemigrations` and `python manage.py migrate`
7. Run program: `python manage.py runserver`.
9. Run test: `python manage.py  test order_inventory_simple.apps.inventories` and `python manage.py  test order_inventory_simple.apps.orders`.
9. Check urls: `python manage.py show_urls`.
