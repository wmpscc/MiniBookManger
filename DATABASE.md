### Admin
```mysql
USE bookmanage;
CREATE TABLE Admin 
(admin_id char(20) primary key,
admin_name char(32),
password char(32),
level char(32));
```