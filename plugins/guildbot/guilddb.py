import logging
import sys
import sqlite3


class GuildDB:

    def __init__(self, dbfile):
        self._dbfile = dbfile
        self.logger = logging.getLogger('ManaChat.Guild')
        self.db, self.cur = self._open_sqlite_db(dbfile)

        # self.cur.execute('PRAGMA foreign_keys = ON')
        self.cur.execute('create table if not exists GUILDS(\
                              ID       integer primary key,\
                              NAME     text[25] not null unique,\
                              CREATED  datetime default current_timestamp,\
                              MOTD     text[100])')
        self.cur.execute('create table if not exists PLAYERS(\
                              ID       integer primary key,\
                              NAME     text[25] not null unique,\
                              LASTSEEN date,\
                              GUILD_ID integer,\
                              ACCESS   integer not null default -10,\
                              SHOWINFO boolean not null default 0,\
                              foreign key(GUILD_ID) references GUILDS(ID))')
        self.db.commit()

    def __del__(self):
        try:
            self.db.close()
        except Exception:
            pass

    def _open_sqlite_db(self, dbfile):
        """
        Open sqlite db, and return tuple (connection, cursor)
        """
        try:
            db = sqlite3.connect(dbfile)
            cur = db.cursor()
        except sqlite3.Error, e:
            self.logger.error("sqlite3 error: %s", e.message)
            sys.exit(1)
        return db, cur

    def guild_create(self, name):
        self.cur.execute('insert into GUILDS(NAME) values(?)', (name,))
        self.db.commit()
        if self.cur.rowcount:
            self.logger.info('Created guild "%s"', name)
            return True
        else:
            self.logger.info('Error creating guild "%s"', name)
            return False

    def guild_delete(self, name):
        self.cur.execute('select ID from GUILDS where name = ?', (name,))
        row = self.cur.fetchone()
        if row:
            guild_id = row[0]
            self.cur.execute('delete from GUILDS where name=?', (name,))
            self.cur.execute('update PLAYERS set GUILD_ID = NULL, \
                              ACCESS = -10, where GUILD_ID = ?', (guild_id,))
            self.db.commit()
            self.logger.info('Deleted guild "%s"', name)
            return True
        else:
            self.logger.error('Guild "%s" not found', name)
            return False

    def guild_set_motd(self, name, motd):
        self.cur.execute('update GUILD set MOTD = ? where NAME = ?',
                         (motd, name))
        self.db.commit()
        if self.cur.rowcount:
            self.logger.info('Guild "%s" MOTD: %s', name, motd)
            return True
        else:
            self.logger.error('Error setting MOTD for guild: %s', name)
            return False

    # NOTE: might need to remove this
    def player_create(self, name, guild_name='', access_level=-10):
        query = '''insert into PLAYERS(NAME, GUILD_ID, ACCESS)
                   values(?, (select ID from GUILDS where NAME = ?), ?)'''
        self.cur.execute(query, (name, guild_name, access_level))

        if self.cur.rowcount > 0:
            self.logger.info('Creted player "%s" in guild "%s" with access %d',
                            name, guild_name, access_level)
        else:
            self.logger.warning('Could not create player "%s"', name)

        self.db.commit()

    def player_info(self, name):
        query = '''select GUILDS.ID,GUILDS.NAME,ACCESS
                   from PLAYERS join GUILDS
                   on PLAYERS.GUILD_ID = GUILDS.ID
                   where PLAYERS.NAME = ?'''
        self.cur.execute(query, (name,))
        return self.cur.fetchone()

    def player_get_access(self, name, guild_name=''):
        query = 'select ACCESS from PLAYERS where NAME = ?'
        self.cur.execute(query, (name, guild_name))
        row = self.cur.fetchone()
        if row:
            return row[0]
        else:
            # self.logger.warning('player %s not found', name)
            return -10

    def player_set_access(self, name, access_level):
        query = '''update table PLAYERS set ACCESS = ?
                   where name = ?'''
        self.cur.execute(query, (name, access_level))
        self.db.commit()

    def player_join_guild(self, player, guild, access=0):
        self.cur.execute('select ID from GUILDS where NAME = ?', (guild,))
        guild_info = self.cur.fetchone()
        if guild_info:
            guild_id = guild_info[0]
        else:
            self.logger.error('Guild "%s" not found', guild)
            return False

        query = '''update or ignore PLAYERS
                   set GUILD_ID = ?, ACCESS = ?
                   where NAME = ?'''
        self.cur.execute(query, (guild_id, access))

        query = '''insert or ignore into
                   PLAYERS(NAME, GUILD_ID, ACCESS)
                   values(?, ?, ?)'''
        self.cur.execute(query, (player, guild_id, access))

        self.db.commit()

        self.logger.info('Added player "%s" to guild "%s"',
                         player, guild)
        return True

    def guild_remove_player(self, player_name):
        query = '''update PLAYERS set GUILD_ID = NULL, ACCESS = -10
                   where NAME = ?'''
        self.cur.execute(query, (player_name,))
        self.db.commit()

    def all_players_same_guild(self, player_name):
        query = '''select NAME from PLAYERS
                   where GUILD_ID = (select GUILD_ID from PLAYERS
                                     where NAME = ?)'''
        return self.cur.execute(query, (player_name,))

    def all_players_any_guild(self):
        query = '''select NAME from PLAYERS
                   where ACCESS >= 0'''
        return self.cur.execute(query)
