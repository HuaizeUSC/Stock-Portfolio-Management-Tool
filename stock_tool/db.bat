echo yes | python .\manage.py flush --no-input --database default
echo yes | python .\manage.py flush --no-input --database mysql1
echo yes | python .\manage.py flush --no-input --database mysql2
echo yes | python .\manage.py flush --no-input --database mysql3
python .\manage.py makemigrations
python .\manage.py migrate --database default
python .\manage.py migrate --database mysql1
python .\manage.py migrate --database mysql2
python .\manage.py migrate --database mysql3

