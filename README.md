# rest-api-neo4j
REST API allowing CRUD functionalities, using Neo4j and Flask

Endpoints:  
	GET /employees - returns all employees  
	GET /employees/by_name/<name> - returns all employees with specified name  
	GET /employees/by_surname/<surname> - returns all employees with specified surname  
	GET /employees/by_position/<surname> - returns all employees with specified position  
	GET /employees/<id> - returns the employee with specified id  
	GET /employees/<id>/department - returns the department of the employee with specified id  
 
  GET /departments - returns all departments  
  GET /departments/by_name/<name> - returns all departments with specified name  
	
  PUT /employees/<id> - edits the employee with specified id (required fields: name: str, surname: str, age: number, position: str)  
	PUT /employees/<id>/department - changes the department the employee is working in (required fields: department: str)  
	
  POST /employees - adds an employee (required fields: name: str, surname: str, age: number, position: str, department: str)  
	name and surname combination must be unique
	

Examples:  
	GET /employees  
![get employees](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/48159bf9-dcb3-4774-bcc4-1a1de4e463d0)  
  GET /employees/by_name/Adam  
![get by name](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/80336eaa-717a-4243-87a5-15f8c9921747)  
  GET /employees/by_surname/Kowalski  
![get by surname](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/9f852efa-6ac4-4b36-be87-75470a9668bb)  
  GET /employees/by_position/Teacher  
![get by position](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/e4f4cfd3-7250-47be-806c-992a8b27b3be)  
  GET /employees/0  
![get by id](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/8ed456dc-2a16-42a8-aa19-8e86d2de226e)  
  GET /employees/0/department  
![get dept](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/fb30c547-1f50-4915-bf8b-5126764f5328)  
  GET /departments  
![get deptartments](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/ec96b6cf-9d56-44d5-a2c7-c1533488f75d)  
  GET /departments/by_name/Wydzial Matematyki, Fizyki i Informatyki UG  
![get deptartments by name](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/14583ee1-55a0-4e5b-bb3c-1c1ff895565d)  
  PUT /employees/0  
![put employees](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/fc710e40-828c-487c-a1c3-504e52d43820)  
  PUT /employees/0/department  
![put dept](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/4b21866e-e2d8-4296-869e-9318bf895769)  
  POST /employees  
![post](https://github.com/mpomirski/rest-api-neo4j/assets/43695467/0712461d-5313-4181-b0c6-10df1f62cafb)
