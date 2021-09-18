import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
print("db drop and create all")
db_drop_and_create_all()
print("db drop and create all END")

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    print("In get Drinks")
    drinks = Drink.query.order_by(Drink.id).all()
    all_drinks = []
    for drink in drinks:
        all_drinks.append(drink.short())

    print("Got drinks ",all_drinks)

    return jsonify({
        'success': True,
        'drinks': all_drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    print("In get Drinks Detail",jwt)
    drinks = Drink.query.order_by(Drink.id).all()
    all_drinks = []
    for drink in drinks:
        all_drinks.append(drink.long())

    print("Got drinks detail",all_drinks)
    return jsonify({
        'success': True,
        'drinks': all_drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    body = request.get_json()
    print("body type",type(body))

    title = body.get('title', None)
    recipe = body.get('recipe', None)
    print("title ", title)
    print("recipe", type(recipe))

    if title is None or recipe is None:
        abort(401)

    jsonObjStr = json.dumps(recipe)
    print("before creating drink jsonObj", jsonObjStr)
    drink = Drink(title=title,recipe=jsonObjStr)
    drink.insert()
    drinks = []
    drinks.append(drink.long())

    return jsonify({
        'success': True,
         'drinks': drinks
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt,drink_id):
    try:
        body = request.get_json()

        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if title is None or recipe is None:
            abort(422)


        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.title = title

        jsonStrObj = json.dumps(recipe)
        print("json obj type ", jsonStrObj)
        drink.recipe = jsonStrObj

        drink.update()
        print("In patch after updagte")
        drinks = []
        drinks.append(drink.long())
        return jsonify({
            'success': True,
             'drinks': drinks
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt,drink_id):
    try:
        print("in delete drinks",drink_id)
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        print("drink ",drink)
        print("drink delete type ",type(drink))
        if drink is None:
            abort(404)

        drink.delete()
        return jsonify({
            'success': True,
             'delete': drink_id
        })
    except Exception as ex:
        print(ex)
        abort(422)



# Error Handling
'''
Example error handling for unprocessable entity
'''



@app.errorhandler(401)
def unauthorized(error):
    print("In unauthorized")
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    print("In forbidden",error)
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    print("In unprocessable",error)
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(error):
    print("erorr in bad_Reqest",error)
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(501)
def not_implemented(error):
    return jsonify({
        "success": False,
        "error": 501,
        "message": "not implemented"
    }), 501


@app.errorhandler(502)
def bad_gateway(error):
    return jsonify({
        "success": False,
        "error": 502,
        "message": "bad gateway"
    }), 502


@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        "success": False,
        "error": 503,
        "message": "service unavailable"
    }), 503


@app.errorhandler(504)
def gateway_timeout(error):
    return jsonify({
        "success": False,
        "error": 504,
        "message": "gateway timeout"
    }), 504


@app.errorhandler(505)
def http_version_unsupported(error):
    return jsonify({
        "success": False,
        "error": 505,
        "message": "http version unsupported"
    }), 505

@app.errorhandler(AuthError)
def auth_error(ex):
    print("In auth error")
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response



'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
