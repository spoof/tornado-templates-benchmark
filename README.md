Template engines benchmark
============================
To run Tornado server:

	python server.py --autoescape=(0|1)

To run benchmark i used: 

	ab -n 10000 -c 1 'http://localhost:8888/tornado/' 

to test Tornado templates or for Jinja2:

	ab -n 10000 -c 1 'http://localhost:8888/jinja/'
	
Jinja 
=====

Without autoescape
------------------

	* Empty template:
		Render time (avg): 0.0093 ms
		Full render time (avg): 0.0494 ms

	* Normal tempalate:
		Render time (avg): 0.0106 ms
		Full render time (avg): 1.4693 ms

Autoescape on
--------------
	* Empty template:
		Render time (avg): 0.0092 ms
		Full render time (avg): 0.0502 ms

	* Normal tempalate:
		Render time (avg): 0.0095 ms
		Full render time (avg): 3.4678 ms
	
	
Tornado
=======

Without autoescape
------------------
	* Empty template
		Render time (avg): 0.0203 ms
		Full render time (avg): 0.0684 ms

	* Normal tempalte
		Render time (avg): 1.2098 ms
		Full render time (avg): 1.2620 ms
		
Autoescape on:
------------------
	* Empty template:
		Render time (avg): 0.0242 ms
		Full render time (avg): 0.0786 ms

	* Normal template:
		Render time (avg): 2.3724 ms
		Full render time (avg): 2.4286 ms
