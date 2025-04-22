docker_metabase_up:
	docker-compose -f docker-compose.metabase.yml up -d --build

docker_app_up:
	docker-compose -f docker-compose.app.yml up -d --build

docker_app_down:
	docker-compose -f docker-compose.app.yml down

backend_run:
	cd backend && source env/bin/activate && 
	
backend_clean_lib:
	 pipreqs backend --force