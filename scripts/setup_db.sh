psql -U postgres << END
DROP DATABASE reservationservice;
CREATE DATABASE reservationservice;
END

python run.py db upgrade 44567dfc2c69
