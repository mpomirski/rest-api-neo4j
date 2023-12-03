from flask import Flask, g, request, abort, request_started
import os
import ast
from flask_restful import Resource, reqparse, Api
from flask_json import FlaskJSON, json_response
from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError
import neo4j.time

load_dotenv(find_dotenv())

app = Flask(__name__)
api = Api(app)
FlaskJSON(app)

# Function taken from neo4j example git repo


def env(key, default=None, required=True):
    """
    Retrieves environment variables and returns Python natives. The (optional)
    default will be returned if the environment variable does not exist.
    """
    try:
        value = os.environ[key]
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value
    except KeyError:
        if default or not required:
            return default
        raise RuntimeError("Missing required environment variable '%s'" % key)


DATABASE_USERNAME = env('MOVIE_DATABASE_USERNAME')
DATABASE_PASSWORD = env('MOVIE_DATABASE_PASSWORD')
DATABASE_URL = env('MOVIE_DATABASE_URL')


driver = GraphDatabase.driver(DATABASE_URL, auth=basic_auth(
    DATABASE_USERNAME, str(DATABASE_PASSWORD)))  # type: ignore

app.config['SECRET_KEY'] = env('SECRET_KEY')


def get_db():
    if 'neo4j_db' not in g:
        g.neo4j_db = driver.session()
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if 'neo4j_db' not in g:
        g.neo4j_db.close()


with app.app_context():
    db = get_db()


def serialize_employee(employee, id):
    return {
        'id': id,
        'name': employee['name'],
        'surname': employee['surname'],
        'age': employee['age'],
        'position': employee['position']
    }


def serialize_department(department, id):
    return {
        'id': id,
        'name': department['name'],
        'short': department['short'],
    }


class EmployeeListByName(Resource):
    def get(self, name):
        def get_employees_by_name(tx, name):
            return list(tx.run(
                '''
                MATCH (employee:Employee {name: $name}) RETURN employee, ID(employee) AS id
                ''', {'name': name}
            ))
        db = get_db()
        result = db.read_transaction(get_employees_by_name, name)
        return [serialize_employee(record['employee'], record['id']) for record in result]


class EmployeeListById(Resource):
    def get(self, id):
        def get_employees_by_name(tx, id):
            return list(tx.run(
                '''
                MATCH (employee:Employee)
                WHERE ID(employee) = $id
                RETURN employee, ID(employee) AS id
                ''', {'id': id}
            ))
        db = get_db()
        result = db.read_transaction(get_employees_by_name, id)
        return [serialize_employee(record['employee'], record['id']) for record in result]


class EmployeeListBySurname(Resource):
    def get(self, surname):
        def get_employees_by_surname(tx, surname):
            return list(tx.run(
                '''
                MATCH (employee:Employee {surname: $surname}) RETURN employee, ID(employee) AS id
                ''', {'surname': surname}
            ))
        db = get_db()
        result = db.read_transaction(get_employees_by_surname, surname)
        return [serialize_employee(record['employee'], record['id']) for record in result]


class EmployeeListByPosition(Resource):
    def get(self, position):
        def get_employees_by_position(tx, position):
            return list(tx.run(
                '''
                MATCH (employee:Employee {position: $position}) RETURN employee, ID(employee) AS id
                ''', {'position': position}
            ))
        db = get_db()
        result = db.read_transaction(get_employees_by_position, position)
        return [serialize_employee(record['employee'], record['id']) for record in result]


class EmployeeList(Resource):
    def get(self):
        def get_employees(tx):
            return list(tx.run(
                '''
                MATCH (employee:Employee) RETURN employee, ID(employee) AS id
                '''
            ))
        db = get_db()
        result = db.read_transaction(get_employees)
        return [serialize_employee(record['employee'], record['id']) for record in result]


class DepartmentList(Resource):
    def get(self):
        def get_departments(tx):
            return list(tx.run(
                '''
                MATCH (department:Department) RETURN department, ID(department) as id
                '''
            ))
        db = get_db()
        result = db.read_transaction(get_departments)
        return [serialize_department(record['department'], record['id']) for record in result]


class DepartmentListByName(Resource):
    def get(self, name):
        def get_departments_by_name(tx, name):
            return list(tx.run(
                '''
                MATCH (department:Department {name: $name}) RETURN department, ID(department) as id
                ''', {'name': name}
            ))
        db = get_db()
        result = db.read_transaction(get_departments_by_name, name)
        return [serialize_department(record['department'], record['id']) for record in result]


class AddEmployee(Resource):
    def post(self):
        db = get_db()
        data = request.get_json()
        name = data.get('name')
        surname = data.get('surname')
        age = data.get('age')
        position = data.get('position')
        department = data.get('department')
        if not name:
            return {'name': 'This field is required'}, 400
        if not surname:
            return {'surname': 'This field is required'}, 400
        if not age:
            return {'age': 'This field is required'}, 400
        if not position:
            return {'position': 'This field is required'}, 400
        if not department:
            return {'department': 'This field is required'}, 400

        def get_employee_by_fullname(tx, name, surname):
            return tx.run(
                '''
                    MATCH (employee:Employee {name: $name, surname: $surname}) RETURN employee
                    ''', {'name': name, 'surname': surname}
            ).single()

        result = db.read_transaction(get_employee_by_fullname, name, surname)
        if result:
            return {'name': 'name already in use', 'surname': 'surname already in use'}

        def create_employee(tx, name, surname, age, position, department):
            return tx.run(
                '''
                MATCH (d:Department {name: $department})
                CREATE (employee:Employee {name: $name, surname: $surname, age: $age, position: $position})-[:WORKS_IN]->(d) RETURN employee
                ''',
                {
                    'name': name,
                    'surname': surname,
                    'age': age,
                    'position': position,
                    'department': department
                }
            ).single()

        results = db.write_transaction(
            create_employee, name, surname, age, position, department)
        employee = results['employee']
        return serialize_employee(employee), 201


class EditEmployeeDepartment(Resource):
    def get(self, id):
        def get_employee_department(tx, id):
            return list(tx.run(
                '''
                MATCH (employee:Employee)-[:WORKS_IN]->(department:Department)
                WHERE ID(employee) = $id
                RETURN department, ID(department) as id
                ''', {'id': id}
            ))
        db = get_db()
        result = db.read_transaction(get_employee_department, id)
        return [serialize_department(record['department'], record['id']) for record in result]

    def put(self, id):
        db = get_db()
        data = request.get_json()
        department = data.get('department')

        if not department:
            return {'department': 'This field is required'}, 400

        def get_employee_by_id(tx, id):
            return tx.run(
                '''
                    MATCH (employee:Employee) 
                    WHERE ID(employee) = $id
                    RETURN employee
                    ''', {'id': id}
            ).single()

        result = db.read_transaction(get_employee_by_id, id)
        if not result:
            return {'id': 'id not found'}

        def update_employee_department(tx, department, id):
            return tx.run(
                '''
                MATCH (employee:Employee)-[r:WORKS_IN]->()
                WHERE ID(employee) = $id
                MATCH (new_dep:Department {name: $department})
                DELETE r
                CREATE (employee)-[:WORKS_IN]->(new_dep)
                RETURN employee, ID(employee) as id
                ''',
                {
                    'department': department,
                    'id': id
                }
            ).single()

        results = db.write_transaction(
            update_employee_department, department, id)
        if not results:
            return {'department': 'department not found'}
        return serialize_employee(results['employee'], results['id']), 201


class EditEmployee(Resource):
    def put(self, id):
        db = get_db()
        data = request.get_json()
        name = data.get('name')
        surname = data.get('surname')
        age = data.get('age')
        position = data.get('position')

        if not name:
            return {'name': 'This field is required'}, 400
        if not surname:
            return {'surname': 'This field is required'}, 400
        if not age:
            return {'age': 'This field is required'}, 400
        if not position:
            return {'position': 'This field is required'}, 400

        def get_employee_by_id(tx, id):
            return tx.run(
                '''
                    MATCH (employee:Employee) 
                    WHERE ID(employee) = $id
                    RETURN employee
                    ''', {'id': id}
            ).single()

        result = db.read_transaction(get_employee_by_id, id)
        if not result:
            return {'id': 'id not found'}

        def update_employee(tx, id, name, surname, age, position):
            return tx.run(
                '''
                MATCH (employee:Employee)
                WHERE ID(employee) = $id
                SET employee.name = $name,
                employee.surname = $surname,
                employee.age = $age,
                employee.position = $position
                RETURN employee, ID(employee) as id
                ''',
                {
                    'id': id,
                    'name': name,
                    'surname': surname,
                    'age': age,
                    'position': position
                }
            ).single()

        results = db.write_transaction(
            update_employee, id, name, surname, age, position)
        return serialize_employee(results['employee'], results['id'])


api.add_resource(EmployeeList, '/employees')
api.add_resource(EmployeeListByName, '/employees/by_name/<string:name>')
api.add_resource(EmployeeListBySurname,
                 '/employees/by_surname/<string:surname>')
api.add_resource(EmployeeListByPosition,
                 '/employees/by_position/<string:position>')
api.add_resource(EditEmployeeDepartment,
                 '/employees/<int:id>/department/')
api.add_resource(EditEmployee,
                 '/employees/<int:id>')
api.add_resource(EmployeeListById, '/employees/<int:id>')
api.add_resource(DepartmentList, '/departments')
api.add_resource(DepartmentListByName, '/departments/by_name/<string:name>')
api.add_resource(AddEmployee, '/employees')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
