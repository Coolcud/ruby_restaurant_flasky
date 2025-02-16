from flask import abort, Blueprint, jsonify, make_response, request
from app import db
from app.models.restaurant import Restaurant
from app.models.employee import Employee

restaurant_bp = Blueprint("restaurant", __name__, url_prefix="/restaurant")

@restaurant_bp.route("", methods=["POST"])
def add_restaurant():
    request_body = request.get_json()
    new_restaurant = Restaurant.from_dict(request_body)

    db.session.add(new_restaurant)
    db.session.commit()

    return {"id": new_restaurant.id}, 201

@restaurant_bp.route("", methods=["GET"])
def get_restaurants():
    response = []
    name_query = request.args.get("name")

    if name_query is None:
        all_restaurants = Restaurant.query.all()
    else:
        all_restaurants = Restaurant.query.filter_by(name=name_query)

    for restaurant in all_restaurants:
        response.append(restaurant.to_dict())

    return jsonify(response), 200

#/restaurant/<id>
@restaurant_bp.route("/<rest_id>", methods=["GET"])
def get_one_restaurant(rest_id):
    restaurant = validate_item(Restaurant, rest_id)

    # if restaurant is None:
    #     return {"message": f"id {restaurant_id} not found"}, 404
    
    return restaurant.to_dict(), 200


@restaurant_bp.route("/<rest_id>", methods=["PUT"])
def update_restaurant(rest_id):
    restaurant = validate_item(Restaurant, rest_id)

    request_data = request.get_json()

    restaurant.name = request_data["name"]
    restaurant.cuisine = request_data["cuisine"]
    restaurant.rating = request_data["rating"]
    restaurant.distance_from_ada = request_data["distance_from_ada"]

    db.session.commit()

    return {"msg": f"restaurant {rest_id} successfully updated"}, 200


@restaurant_bp.route("/<rest_id>", methods=["DELETE"])
def delete_restaurant(rest_id):
    restaurant = validate_item(Restaurant, rest_id)

    db.session.delete(restaurant)
    db.session.commit()

    return {"msg": f"restaurant {rest_id} successfully deleted"}, 200

@restaurant_bp.route("/<rest_id>/employee", methods=["POST"])
def add_employee_to_restaurant(rest_id):
    restaurant = validate_item(Restaurant, rest_id)

    request_body = request.get_json()

    employee = Employee.from_dict(request_body)
    employee.restaurant = restaurant

    db.session.add(employee)
    db.session.commit()

    return jsonify({"msg": f"Created employee with id {employee.id} and attached to {restaurant.id}"}), 201

@restaurant_bp.route("/<rest_id>/employee", methods=["GET"])
def get_all_employees_of_restaurant(rest_id):
    restaurant = validate_item(Restaurant, rest_id)

    employees = [employee.to_dict() for employee in restaurant.employees]

    return jsonify(employees), 200

def validate_item(model, item_id):
    try:
        item_id = int(item_id)
    except ValueError:
        return abort(make_response({"message": f"invalid id: {item_id}"}, 400))
    
    return model.query.get_or_404(item_id)


