import uuid

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import MenuModel, SubmenuModel, DishModel
from models import Menu, Submenu, Dish, UpdatedMenu, SubmenuUpdate, DishUpdate


def create_menu(db: Session, menu: Menu):
    db_menu = MenuModel(title=menu.title, description=menu.description)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return {"id": db_menu.id,"title":db_menu.title, "description":db_menu.description, "submenu_count": 0, "dishes_count":0}


def read_menu(session: Session, menu_id: uuid.UUID):
    db_menu = session.query(MenuModel).filter(MenuModel.id == menu_id).first()
    submenus_count = session.query(func.count(SubmenuModel.id)).filter(SubmenuModel.menu_id == menu_id).scalar() or 0 #агрегационый запрос на подсчёт количества подменю в меню
    submenus_with_dishes = session.query(SubmenuModel.id, SubmenuModel.title, SubmenuModel.description,
                                         func.count(DishModel.id).label("dishes_count")). \
        outerjoin(DishModel, SubmenuModel.id == DishModel.submenu_id). \
        filter(SubmenuModel.menu_id == menu_id). \
        group_by(SubmenuModel.id, SubmenuModel.title, SubmenuModel.description). \
        all()#агрегационый запрос на подсчёт количества блюд в меню

    submenu_info = [{"id": submenu.id, "title": submenu.title, "description": submenu.description,
                     "dishes_count": submenu.dishes_count} for submenu in submenus_with_dishes]

    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    else:
        menu_info = {"id": menu_id, "title": db_menu.title, "description": db_menu.description,
                     "submenus_count": submenus_count, "submenus": submenu_info,
                     "dishes_count": sum(submenu.dishes_count for submenu in submenus_with_dishes)}
        return menu_info


def read_all_menus(session: Session):
    all_menus = session.query(MenuModel).all()
    menus_info = []
    for menu in all_menus:
        submenus_count = session.query(func.count(SubmenuModel.id)).filter(SubmenuModel.menu_id == menu.id).scalar() or 0
        submenus_with_dishes = session.query(SubmenuModel.id, SubmenuModel.title, SubmenuModel.description,
                                             func.count(DishModel.id).label("dishes_count")). \
            outerjoin(DishModel, SubmenuModel.id == DishModel.submenu_id). \
            filter(SubmenuModel.menu_id == menu.id). \
            group_by(SubmenuModel.id, SubmenuModel.title, SubmenuModel.description). \
            all()

        submenu_info = show_submenus(session, menu.id)

        menus_info.append(
            {
                "id": menu.id,
                "title": menu.title,
                "description": menu.description,
                "submenus": submenu_info,
                "submenus_count": submenus_count,
                "dishes_count": sum(submenu.dishes_count for submenu in submenus_with_dishes)
            }
        )
    return menus_info


def update_menu(session: Session, target_menu_id: uuid.UUID, menu: Menu):
    if target_menu_id is None:
        raise HTTPException(status_code=400, detail="Invalid target_menu_id")
    db_menu = session.query(MenuModel).filter(MenuModel.id == target_menu_id).first()
    if db_menu is not None:
        if menu and menu.title:
            db_menu.title = menu.title
        if menu and menu.description:
            db_menu.description = menu.description
        session.commit()
        session.refresh(db_menu)
        return UpdatedMenu(
            id=str(db_menu.id),
            title=db_menu.title,
            description=db_menu.description
        )
    else:
        raise HTTPException(status_code=404, detail="Menu not found")


def delete_menu(session: Session, menu_id: uuid.UUID):
    db_menu = session.query(MenuModel).filter(MenuModel.id == menu_id).first()
    if db_menu:
        for submenu in db_menu.submenus:
            session.delete(submenu)
        session.delete(db_menu)
        session.commit()
        return {"message": "successful"}
    return {"message": "error"}


from sqlalchemy import func


def show_submenus(session: Session, api_test_menu_id: uuid.UUID):
    menu = session.query(MenuModel).filter(MenuModel.id == api_test_menu_id).first()
    if menu is None:
        return []
    submenu_info = []
    for submenu in menu.submenus:
        dishes_count = session.query(func.count(DishModel.id)).filter(DishModel.submenu_id == submenu.id).scalar() or 0

        submenu_dishes = []
        for dish in submenu.dishes:
            submenu_dishes.append(
                {"id": dish.id, "title": dish.title, "description": dish.description, "price": dish.price})

        submenu_info.append({
            "id": submenu.id,
            "title": submenu.title,
            "description": submenu.description,
            "dishes": submenu_dishes,
            "dishes_count": dishes_count
        })
    return submenu_info


def create_submenu(session: Session, menu_id: uuid.UUID, submenu: Submenu):
    nw_submenu = SubmenuModel(title=submenu.title, description=submenu.description)
    dishes_count = session.query(func.count(DishModel.id)).filter(DishModel.submenu_id == nw_submenu.id).scalar() or 0
    db_menu = session.query(MenuModel).filter(MenuModel.id == menu_id).first()
    if db_menu is None:
        return []
    for existing_submenu in db_menu.submenus:
        if existing_submenu.title == nw_submenu.title:
            raise HTTPException(status_code=400, detail="Submenu with the same title already exists in this menu")
    db_menu.submenus.append(nw_submenu)
    session.add(nw_submenu)
    session.commit()
    return {"id": nw_submenu.id, "title": nw_submenu.title,
            "description": nw_submenu.description,
            "dishes_count": dishes_count}


def show_submenu(session:Session,api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID):
    menu = session.query(MenuModel).filter(MenuModel.id == api_test_menu_id).first()
    for a in menu.submenus:
        if a.id == submenu_id:
            dishes_count = session.query(func.count(DishModel.id)).filter(
                DishModel.submenu_id == submenu_id).scalar() or 0
            submenu_info = {"id": a.id, "title": a.title, "description": a.description, "dishes_count": dishes_count}
            dishes_info = [{"id": dish.id, "title": dish.title, "description": dish.description,
                            "price": "{:.2f}".format(round(float(dish.price), 2))} for dish in a.dishes]
            submenu_info["dishes"] = dishes_info
            return submenu_info
    raise HTTPException(status_code=404, detail="submenu not found")



def update_submenu(session:Session, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, submenu: SubmenuUpdate):
    menu = session.query(MenuModel).filter(MenuModel.id == api_test_menu_id).first()
    if menu is not None:
        for a in menu.submenus:
            if a.id == submenu_id:
                if submenu.title:
                    for existing_submenu in menu.submenus:
                        if existing_submenu.id != submenu_id and existing_submenu.title == submenu.title:
                            raise HTTPException(status_code=400,
                                                detail="Submenu with the same title already exists in this menu")
                    a.title = submenu.title
                if submenu.description:
                    a.description = submenu.description
                session.commit()
                session.refresh(a)
                return {"id": a.id, "title": a.title, "description": a.description}
        raise HTTPException(status_code=404, detail="Submenu not found")
    raise HTTPException(status_code=404, detail="Menu not found")

def delete_submenu(session: Session, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID):
    menu = session.query(MenuModel).filter(MenuModel.id == api_test_menu_id).first()
    for i, submenu in enumerate(menu.submenus):
        if submenu.id == submenu_id:
            for dish in submenu.dishes:
                session.delete(dish)
            session.delete(submenu)
            session.commit()
            return {"message": "successful delete"}
    raise HTTPException(status_code=404, detail="submenu not found")


def show_dishes(session: Session, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID):
    menu = session.query(SubmenuModel).filter(
        SubmenuModel.id == submenu_id and SubmenuModel.menu_id == api_test_menu_id).first()
    if menu is None:
        return []
    dishes_info = []
    for dish in menu.dishes:
        dishes_info.append({"id": dish.id, "title": dish.title, "description": dish.description,
                            "price": "{:.2f}".format(round(float(dish.price), 2))})
    return dishes_info


def new_dish(session: Session, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, dish: Dish):
    nw_dish = DishModel(title=dish.title, description=dish.description, price=dish.price)
    submenu = session.query(SubmenuModel).filter(
        SubmenuModel.id == submenu_id and SubmenuModel.menu_id == api_test_menu_id).first()
    if submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    for existing_dish in submenu.dishes:
        if existing_dish.title == dish.title:
            raise HTTPException(status_code=400, detail="Dish with the same name already exists in this submenu")
    submenu.dishes.append(nw_dish)
    session.add(nw_dish)
    session.commit()
    return {"id": nw_dish.id, "title": nw_dish.title, "description": nw_dish.description,
            "price": "{:.2f}".format(round(float(nw_dish.price), 2))}


def show_dish(session: Session, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID):
    submenu = session.query(SubmenuModel).filter(
        SubmenuModel.id == submenu_id and SubmenuModel.menu_id == api_test_menu_id).first()
    for a in submenu.dishes:
        if a.id == dish_id:
            return {"id": a.id, "title": a.title, "description": a.description,
                    "price": "{:.2f}".format(round(float(a.price), 2))}
    raise HTTPException(status_code=404, detail="dish not found")


def update_dish(session: Session, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID,
                dish: DishUpdate):
    submenu = session.query(SubmenuModel).filter(
        SubmenuModel.id == submenu_id and SubmenuModel.menu_id == api_test_menu_id).first()
    if submenu is not None:
        for a in submenu.dishes:
            if a.id == dish_id:
                if dish.title:
                    for existing_dish in submenu.dishes:
                        if existing_dish.id != dish_id and existing_dish.title == dish.title:
                            raise HTTPException(status_code=400,
                                                detail="Dish with the same title already exists in this submenu")
                    a.title = dish.title
                if dish.description:
                    a.description = dish.description
                if dish.price:
                    a.price = "{:.2f}".format(round(float(dish.price), 2))
                session.commit()
                session.refresh(a)
                return {"id": a.id, "title": a.title, "description": a.description,
                        "price": "{:.2f}".format(round(float(a.price), 2))}
        raise HTTPException(status_code=404, detail="Dish not found")
    raise HTTPException(status_code=404, detail="Submenu not found")


def delete_dish(session: Session, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID):
    submenu = session.query(SubmenuModel).filter(
        SubmenuModel.id == submenu_id and SubmenuModel.menu_id == api_test_menu_id).first()
    for a in submenu.dishes:
        if a.id == dish_id:
            session.delete(a)
            session.commit()
            return {"message": "dish was deleted successful"}
    raise HTTPException(status_code=404, detail="dish not found")
