import os
from flask import Flask, request, abort, jsonify
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, get_token_auth_header, check_permissions, verify_decode_jwt, requires_auth

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    db_drop_and_create_all()
    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    '''
    ## ROUTES
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
        try:
            drinks_objects= Drink.query.all()
            drinks=[drink.short() for drink in drinks_objects]
            return jsonify({'success': True, "drinks": drinks}), 200
        except:
            abort(400)

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
    def drinks_detail(payload):
        try:
            drinks_objects= Drink.query.all()
            drinks=[drink.long() for drink in drinks_objects]
            return jsonify({'success': True, "drinks": drinks}), 200
        except:
            abort(400)

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
    @requires_auth(permission="post:drinks")
    def post_drink(payload):
        try:
            req_title = str(request.get_json()['title'])
            req_recipe = request.get_json()['recipe']
            recipe_str = json.dumps(req_recipe)
            drink = Drink(title=req_title, recipe=recipe_str)
            drink.insert()
            drink_detail = drink.long()
            return jsonify({"success": True, "drinks": drink_detail}), 200
        except:
            abort(400)

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
    @app.route('/drinks/<id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def patch_drink(payload, id):
        try:
            req_title = request.get_json()['title']
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = req_title
            drink.update()
            drink_detail = [drink.long()]
            return jsonify({"success": True, "drinks": drink_detail}), 200
        except:
            abort(404)

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
    @app.route('/drinks/<id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(payload, id):
        drink_delete = Drink.query.filter(Drink.id == id).one_or_none()
        if drink_delete:
            drink_delete.delete()
            return jsonify({'success': True, "delete": id}), 200
        else:
            abort(404)

    ## Error Handling
    '''
    Example error handling for unprocessable entity
    '''
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False, 
                        "error": 422,
                        "message": "unprocessable"
                        }), 422

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
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False,
        'error': 404,
        'message': 'Not Found :('  }), 404


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False,
        'error': 400,
        'message': 'Bad request :('  }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'success': False,
        'error': 405,
        'message': 'Method not allowed :('  }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'success': False,
        'error': 500,
        'message': 'Server Error :('  }), 500

    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above 
    '''
    @app.errorhandler(AuthError)
    def Auth_Error(error):
        return jsonify(error.error), error.status_code
    
    return app