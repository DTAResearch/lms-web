#!/bin/sh

#Start cron
service cron start

#Start Fast API server
uvicorn main:app --host 0.0.0.0 --port 8000

# Đồng bộ dữ liệu
python backend\app\jobs\sync_chat.py & python backend\app\jobs\sync_model.py & python backend\app\jobs\sync_user.py

uvicorn main:app --reload --port 8000 

docker exec -it lms-learn-with-ai-cron-1 /bin/bash run_sync_job.sh"

https://metabase.hoctiep.com/dashboard/5-lsm-report-sv?date=&models=gia-s-bit-tut&t%25C3%25AAn_m%25C3%25B4_h%25C3%25ACnh=&user_id=30de9ef6-a9fd-41a9-8420-74064da4d7d5

