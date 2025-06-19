## backup.sql
백업파일 -> 로컬 : mysql -u root -p < {경로}/backup.sql
로컬 -> 백업 : mysqldump -u root -p --databases GigachadDb > backup.sql

로 db 로컬에 설정해놓으면 됩니다.
