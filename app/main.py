from fastapi import FastAPI, Depends
from database import Session as db_session
from database import clear_database
from crud import *

app = FastAPI()


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()

def clear_db_on_startup():
    with db_session() as db:
        clear_database(db)


clear_db_on_startup()

@app.post("/api/v1/menus/", status_code=201)
def create_new_menu(menu: Menu, db: Session = Depends(get_db)):
    db_menu = create_menu(db, menu)
    return db_menu


@app.get("/api/v1/menus/{menu_id}")
def get_menu(menu_id: uuid.UUID, db: Session = Depends(get_db)):
    return read_menu(db, menu_id)


@app.get("/api/v1/menus/")
def get_all_menus(db: Session = Depends(get_db)):
    db_menus = read_all_menus(db)
    return db_menus


@app.patch("/api/v1/menus/{menu_id}")
def update_concreate_menu(menu_id: uuid.UUID, updated_menu: Menu, db: Session = Depends(get_db)):
    return update_menu(db, menu_id, updated_menu)


@app.delete("/api/v1/menus/{menu_id}")
def delete_concreate_menu(menu_id: uuid.UUID, db: Session = Depends(get_db)):
    return delete_menu(db, menu_id)


@app.post("/api/v1/menus/{menu_id}/submenus", status_code=201)
def create_new_submenu(menu_id: uuid.UUID, submenu: Submenu, db: Session = Depends(get_db)):
    db_submenu = create_submenu(db, menu_id, submenu)
    return db_submenu


@app.get("/api/v1/menus/{menu_id}/submenus")
def get_all_submenus(menu_id: uuid.UUID, db: Session = Depends(get_db)):
    db_submenus = show_submenus(db,menu_id)
    return db_submenus

@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def get_concreate_submenu(menu_id: uuid.UUID, submenu_id:uuid.UUID, db: Session = Depends(get_db)):
    return show_submenu(db,menu_id,submenu_id)
@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def update_existing_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, updated_submenu: SubmenuUpdate,
                            db: Session = Depends(get_db)):
    return update_submenu(db,menu_id,submenu_id,updated_submenu)

@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def delete_existing_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, db: Session = Depends(get_db)):
    return delete_submenu(db, menu_id, submenu_id)


@app.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", status_code=201)
def create_new_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish: Dish, db: Session = Depends(get_db)):
    db_dish = new_dish(db,menu_id, submenu_id, dish)
    return db_dish

@app.get("/api/v1/menus/{api_test_menu_id}/submenus/{submenu_id}/dishes")
def show_all_dishes(api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, db:Session = Depends(get_db)):
    return show_dishes(db, api_test_menu_id,submenu_id)

@app.get("/api/v1/menus/{api_test_menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def show_concreate_dish(api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID, db:Session = Depends(get_db)):
    return show_dish(db, api_test_menu_id,submenu_id,dish_id)

@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def update_existing_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID, updated_dish: DishUpdate,
                         db: Session = Depends(get_db)):
    return update_dish(db, menu_id, submenu_id, dish_id, updated_dish)


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def delete_existing_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID, db: Session = Depends(get_db)):
    return delete_dish(db,menu_id,submenu_id,dish_id)

