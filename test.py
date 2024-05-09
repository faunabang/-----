import os

# 데이터베이스 파일 경로
db_path = 'gaia_parameters.db'

# 파일이 존재하는지 확인하고 삭제
if os.path.exists(db_path):
    os.remove(db_path)
    print("Database removed successfully.")
else:
    print("The file does not exist.")
