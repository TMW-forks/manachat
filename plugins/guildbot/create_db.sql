pragma foreign_keys=on;

create table if not exists GUILDS(
    ID       integer primary key not null,
    NAME     text[25] not null unique,
    CREATED  datetime default current_timestamp,
    MOTD     text[100]);

create table if not exists PLAYERS(
    ID       integer primary key not null,
    NAME     text[25] not null unique,
    LASTSEEN datetime,
    GUILD_ID integer,
    ACCESS   integer default 0,
    foreign key(GUILD_ID) references GUILDS(ID));

insert into GUILDS(NAME) values('Crew of Red Corsair');
insert into GUILDS(NAME) values('Phoenix Council');

insert into PLAYERS(NAME, GUILD_ID, ACCESS) values('Travolta', 1, 10);
insert into PLAYERS(NAME, GUILD_ID, ACCESS) values('Rill', 1, 10);
insert into PLAYERS(NAME, GUILD_ID, ACCESS) values('veryape', 2, 10);

