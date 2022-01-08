drop database if exists grouptogetherdb;
create database grouptogetherdb;
use grouptogetherdb;

create table users (
	chat_id int not null primary key,
    name varchar(255) not null
);

create table looking_for_group (
	chat_id int NOT NULL,
    school varchar(100) NOT NULL,
    module_code varchar(100) NOT NULL,
    semester int NOT NULL,
    section varchar(100) NOT NULL,
    
    constraint primary key (chat_id,school,module_code,semester)
);

create table looking_for_members (
	chat_id int NOT NULL,
    school varchar(100) NOT NULL,
    module_code varchar(100) NOT NULL,
    semester int NOT NULL,
    section varchar(100) NOT NULL,
    num_members_need int NOT NULL,
    
    constraint primary key (chat_id,school,module_code,semester)
);

create table match_found (
	finder_chat_id int NOT NULL,
    looker_chat_id int NOT NULL,
    school varchar(100) NOT NULL,
    module_code varchar(100) NOT NULL,
    semester int NOT NULL,
    section varchar(100) NOT NULL,
    accepted char(1) NOT NULL, # P- Pending, A - Accepted, R - rejected
    
    constraint primary key (finder_chat_id,looker_chat_id,school,module_code,semester)
);
