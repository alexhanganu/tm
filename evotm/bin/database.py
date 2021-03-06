from sqlite3 import connect, OperationalError
from os import environ, path
from time import strftime, localtime, gmtime
from .utils import DEFAULT


TABLES = {
    'Tabs'                     : ('tab_id',         'position'),
    'Database'                 : ('day_of_week_id', 'date_id', 'task_id', 'duration_id', 'starttime_id'),
    'Dailydatabase'            : ('day_of_week_id', 'date_id', 'task_id', 'duration_id'),
    'DailyStartTime'           : ('date_id',        'task_id', 'starttime_id'),
    'Projects'                 : ('project_id',     'task_id'),
    'MainDailyGroups'          : ('dailygroup_id',  'task_id'),
    'PausedTasks'              : ('dailygroup_id',  'task_id'),
    'ArchivedTasks'            : ('dailygroup_id',  'task_id'),
    'Days_task_active'         : ('task_id',        'days_task_active_id'),
    'MinDailyTaskDuration'     : ('task_id',        'min_duration_id'),
    'Date_deadline'            : ('task_id',        'date_id'),
    'MainDailyGroups_bg_color' : ('dailygroup_id',  'color_id'),
}


class DB:
    def __init__(self, credentials_home):
        self.home = credentials_home

    def __connect_db__(self):
        db = path.join(self.home, 'evotm.db')
        conn = connect(db, check_same_thread=False)
        try:
            self.__get_table_(conn)
        except OperationalError:
            self.__create_table__(conn)
        return conn
    def __get_table_(self, conn):
        ls_tables = []
        for table in conn.execute('''SELECT * FROM sqlite_master WHERE type='table' ''').fetchall():
            ls_tables.append(table[1])
        if len(ls_tables) == 10:
            pass
        else:
            self.__create_table__(conn)
        return ls_tables
    def __create_table__(self, conn):
        for table in TABLES:
                conn.execute('''CREATE TABLE if not exists {} {}'''.format(table, TABLES[table]))

        # conn.execute('''CREATE TABLE if not exists Tabs (tab_id, position)''')
        # conn.execute('''CREATE TABLE if not exists Database (day_of_week_id, date_id, task_id, duration_id, starttime_id)''')
        # conn.execute('''CREATE TABLE if not exists MainDailyGroups (dailygroup_id, task_id)''')
        # conn.execute('''CREATE TABLE if not exists Projects (project_id, task_id)''')
        # conn.execute('''CREATE TABLE if not exists Days_task_active (task_id, days_task_active_id)''')
        # conn.execute('''CREATE TABLE if not exists MinDailyTaskDuration (task_id, min_duration_id)''')
        # conn.execute('''CREATE TABLE if not exists Date_deadline (task_id, date_id)''')
        # conn.execute('''CREATE TABLE if not exists PausedTasks (dailygroup_id, task_id)''')
        # conn.execute('''CREATE TABLE if not exists ArchivedTasks (dailygroup_id, task_id)''')
        # conn.execute('''CREATE TABLE if not exists Dailydatabase (day_of_week_id, date_id, task_id, duration_id)''')
        # conn.execute('''CREATE TABLE if not exists DailyStartTime (date_id, task_id, starttime_id)''')
        # conn.execute('''CREATE TABLE if not exists MainDailyGroups_bg_color (dailygroup_id, color_id)''')
        if conn.execute('''SELECT count(*) from Tabs ''').fetchone()[0] == 0:
            print('len Tabs is zero, creating tab')
            conn.execute('''INSERT INTO Tabs VALUES(?,?)''', [DEFAULT.tab1,'0'])
        conn.commit()

    def Update_DB(self):
        conn = self.__connect_db__()
        for row in conn.execute('''SELECT * FROM Dailydatabase''').fetchall():
            task = row[2]
            start_time = ''
            if conn.execute('''SELECT count(*) from DailyStartTime where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
                start_time = conn.execute('''SELECT starttime_id from DailyStartTime where task_id="{0}" '''.format(task,)).fetchone()[0]
            data = [(row[0], row[1], task, str(strftime('%H:%M:%S', gmtime(float(row[3])))), start_time)]
            print('inserting into Database values: ',data)
            conn.executemany('''INSERT INTO Database VALUES(?,?,?,?,?)''', data)
        conn.execute('''DELETE FROM Dailydatabase''')
        conn.execute('''DELETE FROM DailyStartTime''')
        conn.commit()

    def UpdateDailyTask(self, task, duration):
        conn = self.__connect_db__()
        if conn.execute('''SELECT count(*) from Dailydatabase where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
            time_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
            new_time = time_in_db+ duration
            conn.execute('''UPDATE Dailydatabase SET duration_id = {0} WHERE task_id= "{1}"'''.format(new_time, task))
        else:
            data = [(str(strftime('%a', localtime())), str(strftime('%Y%m%d', localtime())), task, duration)]
            conn.executemany('''INSERT INTO Dailydatabase VALUES(?,?,?,?)''', data)
        conn.commit()

    def UpdateStartTime(self, task, starttime):
        conn = self.__connect_db__()
        if conn.execute('''SELECT count(*) from DailyStartTime where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
            conn.execute('''UPDATE DailyStartTime SET starttime_id = "{0}" WHERE task_id= "{1}"'''.format(starttime, task))
        else:
            data = [(str(strftime('%Y%m%d', localtime())), task, starttime)]
            conn.executemany('''INSERT INTO DailyStartTime VALUES(?,?,?)''', data)
        conn.commit()


    def __update_table__(self, table, col2update, new_value, where2update, where_value):
        conn = self.__connect_db__()
        conn.execute("UPDATE {0} SET {1} = '{2}' WHERE {3}='{4}'".format(table, col2update, new_value, where2update, where_value))
        conn.commit()


    def SetDailyTaskDuration(self, task, duration):
        conn = self.__connect_db__()
        if conn.execute('''SELECT count(*) from Dailydatabase where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
            conn.execute('''UPDATE Dailydatabase SET duration_id = {0} WHERE task_id= "{1}"'''.format(duration, task))
        else:
            new_time = duration
            data = [(str(strftime('%a', localtime())), str(strftime('%Y%m%d', localtime())), task, new_time)]
            conn.executemany('''INSERT INTO Dailydatabase VALUES(?,?,?,?)''', data)
        conn.commit()

    def update_db_from_pandas(self, dfsql):
        import pandas.io.sql as pdsql
        conn = self.__connect_db__()
        pdsql.to_sql(dfsql, 'Database', conn, if_exists='append', index=False)
        print('dfsql added to database')
        conn.commit()



    def __insert_in_table__(self, table, group, task):
        conn = self.__connect_db__()
        values = [group, task,]
        conn.execute("INSERT INTO {0} VALUES ({1})".format(table,','.join('\"' + str(x) + '\"'for x in values)))
        conn.commit()
       


    def ComputeTaskDuration(self, task):
        conn = self.__connect_db__()
        # date = str(strftime('%Y%m%d', localtime()))
        _TotalTaskDuration = 0
        if self.task_in_table('Dailydatabase', task):
            duration_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
            _TotalTaskDuration = float(duration_in_db)+ _TotalTaskDuration
        return (_TotalTaskDuration)



    def ComputeProjectDuration(self, project):
        MainDailyGroups = self.get_tasks_for_table_('MainDailyGroups')
        conn = self.__connect_db__()
        _TotalProjectDuration_in_db = 0
        for task in MainDailyGroups[project]:
            if task == 'sleep':
                pass
            else:
                if self.task_in_table('Dailydatabase', task):
                    duration_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
                    _TotalProjectDuration_in_db = float(duration_in_db)+ _TotalProjectDuration_in_db
        return _TotalProjectDuration_in_db



    def get_tasks_duration_for_Dailydatabase(self):
        conn = self.__connect_db__()
        table = {}
        for task in conn.execute('''SELECT task_id FROM Dailydatabase''').fetchall():
            table[task[0]] = str(strftime('%H:%M:%S', gmtime(float(conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task[0])).fetchone()[0]))))
        return table

    def task_in_table(self, table, task):
        conn = self.__connect_db__()
        exists = conn.execute('''SELECT count(*) from {0} where task_id="{1}"'''.format(table,task)).fetchone()[0] != 0
        return exists

    def task_and_date_in_table(self, table, task, date):
        conn = self.__connect_db__()
        exists = conn.execute('''SELECT count(*) from {0} where task_id="{1}" and date_id="{2}"'''.format(table,task,date)).fetchone()[0] != 0
        return exists

    def get_values_for_task_(self, table, task, column):
        conn = self.__connect_db__()
        data = conn.execute('''SELECT * from {0} WHERE task_id="{1}" ORDER BY {2} DESC'''.format(table, task, column))
        return data.fetchall()


    def retrieve_all_data(self, file_2save):
        import pandas as pd
        conn = self.__connect_db__()
        df = pd.read_sql('''SELECT * from Database''',conn)
        df.to_csv(file_2save, encoding='utf-8', index=False)


    def get_tasks_for_table_(self, table_name):
        conn = self.__connect_db__()
        cursor = conn.execute('''SELECT * FROM {0}'''.format(table_name,))
        all_data_for_table = cursor.fetchall()        
        table = {}
        if table_name == 'MainDailyGroups':
            for tab in self.get_tasks_for_table_("Tabs"):
                table[tab] = []
        for Group in all_data_for_table:
            if table_name in ['MainDailyGroups','PausedTasks','ArchivedTasks','Projects']:
                if Group[0] not in table:
                    table[Group[0]] = []
                table[Group[0]].append(Group[1])
            elif table_name == 'Dailydatabase':
                table[Group[2]] = []
                table[Group[2]].append(Group)
            else:
                table[Group[0]] = Group[1]
        return table


    def __delete_from_table__(self, table, value1, value2):
        conn = self.__connect_db__()
#        conn.execute("DELETE from {0} WHERE {1}='{2}' AND {3}='{4}'".format(table, TABLES[table][0], value1, TABLES[table][1], value2))

        if table == 'MainDailyGroups' or table == 'PausedTasks' or table == 'ArchivedTasks':
            col1 = 'dailygroup_id'
            col2 = 'task_id'
        elif table == 'Projects':
            col1 = 'project_id'
            col2 = 'task_id'
        elif table == 'Date_deadline':
            col1 = 'task_id'
            col2 = 'date_id'
        elif table == 'Days_task_active':
            col1 = 'task_id'
            col2 = 'days_task_active_id'
        elif table == 'MinDailyTaskDuration':
            col1 = 'task_id'
            col2 = 'min_duration_id'
        elif table == 'MainDailyGroups_bg_color':
            col1 = 'dailygroup_id'
            col2 = 'color_id'
        elif table == 'Tabs':
            col1 = 'tab_id'
            col2 = 'position'
        conn.execute("DELETE from {0} WHERE {1}='{2}' AND {3}='{4}'".format(table, col1, value1, col2, value2))
        conn.commit()


    def close_db(self):
        conn = self.__connect_db__()
        conn.commit()
        conn.close()
        print('database closed')


'''
MOVING ALL TO CLASS
'''
# from setup.get_credentials_home import _get_credentials_home

# def __connect_db__():
#     db = path.join(_get_credentials_home(), 'tm.db')
#     conn = connect(db, check_same_thread=False)
#     try:
#         __get_table_(conn)
#     except OperationalError:
#         __create_table__(conn)
#     return conn


# def Update_DB():
#     conn = __connect_db__()
#     for row in conn.execute('''SELECT * FROM Dailydatabase''').fetchall():
#         task = row[2]
#         start_time = ''
#         if conn.execute('''select count(*) from DailyStartTime where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
#             start_time = conn.execute('''select starttime_id from DailyStartTime where task_id="{0}" '''.format(task,)).fetchone()[0]
#         data = [(row[0], row[1], task, str(strftime('%H:%M:%S', gmtime(float(row[3])))), start_time)]
#         print('inserting into Database values: ',data)
#         conn.executemany('''INSERT INTO Database VALUES(?,?,?,?,?)''', data)
#     conn.execute('''DELETE FROM Dailydatabase''')
#     conn.execute('''DELETE FROM DailyStartTime''')
#     conn.commit()


# def get_tasks_duration_for_Dailydatabase():
#     conn = __connect_db__()
#     table = {}
#     for task in conn.execute('''SELECT task_id FROM Dailydatabase''').fetchall():
#         table[task[0]] = str(strftime('%H:%M:%S', gmtime(float(conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task[0])).fetchone()[0]))))
#     return table


# def UpdateDailyTask(task, duration):
#     conn = __connect_db__()
#     if conn.execute('''select count(*) from Dailydatabase where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
#         time_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
#         new_time = time_in_db+ duration
#         conn.execute('''UPDATE Dailydatabase SET duration_id = {0} WHERE task_id= "{1}"'''.format(new_time, task))
#     else:
#         data = [(str(strftime('%a', localtime())), str(strftime('%Y%m%d', localtime())), task, duration)]
#         conn.executemany('''INSERT INTO Dailydatabase VALUES(?,?,?,?)''', data)
#     conn.commit()


# def UpdateStartTime(task, starttime):
#     conn = __connect_db__()
#     if conn.execute('''select count(*) from DailyStartTime where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
#         conn.execute('''UPDATE DailyStartTime SET starttime_id = "{0}" WHERE task_id= "{1}"'''.format(starttime, task))
#     else:
#         data = [(str(strftime('%Y%m%d', localtime())), task, starttime)]
#         conn.executemany('''INSERT INTO DailyStartTime VALUES(?,?,?)''', data)
#     conn.commit()


# def SetDailyTaskDuration(task, duration):
#     conn = __connect_db__()
#     if conn.execute('''select count(*) from Dailydatabase where task_id="{0}" '''.format(task,)).fetchone()[0] != 0:
#         conn.execute('''UPDATE Dailydatabase SET duration_id = {0} WHERE task_id= "{1}"'''.format(duration, task))
#     else:
#         new_time = duration
#         data = [(str(strftime('%a', localtime())), str(strftime('%Y%m%d', localtime())), task, new_time)]
#         conn.executemany('''INSERT INTO Dailydatabase VALUES(?,?,?,?)''', data)
#     conn.commit()


# def ComputeTaskDuration(task):
#     conn = __connect_db__()
#     # date = str(strftime('%Y%m%d', localtime()))
#     _TotalTaskDuration = 0
#     if task_in_table('Dailydatabase', task):
#         duration_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
#         _TotalTaskDuration = float(duration_in_db)+ _TotalTaskDuration
#     return (_TotalTaskDuration)



# def ComputeProjectDuration(project):
#     MainDailyGroups = get_tasks_for_table_('MainDailyGroups')
#     conn = __connect_db__()
#     _TotalProjectDuration_in_db = 0
#     for task in MainDailyGroups[project]:
#         if task == 'sleep':
#             pass
#         else:
#             if task_in_table('Dailydatabase', task):
#                 duration_in_db = conn.execute('''SELECT duration_id FROM Dailydatabase WHERE task_id="{0}" '''.format(task,)).fetchone()[0]
#                 _TotalProjectDuration_in_db = float(duration_in_db)+ _TotalProjectDuration_in_db
#     return _TotalProjectDuration_in_db


# def task_in_table(table, task):
#     conn = __connect_db__()
#     exists = conn.execute('''select count(*) from {0} where task_id="{1}"'''.format(table,task)).fetchone()[0] != 0
#     return exists

# def task_and_date_in_table(table, task, date):
#     conn = __connect_db__()
#     exists = conn.execute('''select count(*) from {0} where task_id="{1}" and date_id="{2}"'''.format(table,task,date)).fetchone()[0] != 0
#     return exists


# def get_tasks_for_table_(table_name):
#     conn = __connect_db__()
#     cursor = conn.execute('''SELECT * FROM {0}'''.format(table_name,))
#     all_data_for_table = cursor.fetchall()        
#     table = {}
#     if table_name == 'MainDailyGroups':
#         for tab in get_tasks_for_table_("Tabs"):
#             table[tab] = []
#     for Group in all_data_for_table:
#         if table_name in ['MainDailyGroups','PausedTasks','ArchivedTasks','Projects']:
#             if Group[0] not in table:
#                 table[Group[0]] = []
#             table[Group[0]].append(Group[1])
#         elif table_name == 'Dailydatabase':
#             table[Group[2]] = []
#             table[Group[2]].append(Group)
#         else:
#             table[Group[0]] = Group[1]
#     return table


# def update_db_from_pandas(dfsql):
#     import pandas.io.sql as pdsql
#     conn = __connect_db__()
#     pdsql.to_sql(dfsql, 'Database', conn, if_exists='append', index=False)
#     print('dfsql added to database')
#     conn.commit()


# def get_values_for_task_(table, task, column):
#     conn = __connect_db__()
#     data = conn.execute('''SELECT * from {0} WHERE task_id="{1}" ORDER BY {2} DESC'''.format(table, task, column))
#     return data.fetchall()


# def retrieve_all_data(file_2save):
#     import pandas as pd
#     conn = __connect_db__()
#     df = pd.read_sql('''SELECT * from Database''',conn)
#     df.to_csv(file_2save, encoding='utf-8', index=False)


# def __insert_in_table__(table, group, task):
#     conn = __connect_db__()
#     values = [group, task,]
#     conn.execute("INSERT INTO {0} VALUES ({1})".format(table,','.join('\"' + str(x) + '\"'for x in values)))
#     conn.commit()
   

# def __update_table__(table, col2update, new_value, where2update, where_value):
#     conn = __connect_db__()
#     conn.execute("UPDATE {0} SET {1} = '{2}' WHERE {3}='{4}'".format(table, col2update, new_value, where2update, where_value))
#     conn.commit()


# def __delete_from_table__(table, value1, value2):
#     conn = __connect_db__()
#     if table == 'MainDailyGroups' or table == 'PausedTasks' or table == 'ArchivedTasks':
#         col1 = 'dailygroup_id'
#         col2 = 'task_id'
#     elif table == 'Projects':
#         col1 = 'project_id'
#         col2 = 'task_id'
#     elif table == 'Date_deadline':
#         col1 = 'task_id'
#         col2 = 'date_id'
#     elif table == 'Days_task_active':
#         col1 = 'task_id'
#         col2 = 'days_task_active_id'
#     elif table == 'MinDailyTaskDuration':
#         col1 = 'task_id'
#         col2 = 'min_duration_id'
#     elif table == 'MainDailyGroups_bg_color':
#         col1 = 'dailygroup_id'
#         col2 = 'color_id'
#     elif table == 'Tabs':
#         col1 = 'tab_id'
#         col2 = 'position'
#     conn.execute("DELETE from {0} WHERE {1}='{2}' AND {3}='{4}'".format(table, col1, value1, col2, value2))
#     conn.commit()


# def __close_db_():
#     conn = __connect_db__()
#     conn.commit()
#     conn.close()
#     print('database closed')


# def __get_table_(conn):
#     ls_tables = []
#     for table in conn.execute('''SELECT * FROM sqlite_master WHERE type='table' ''').fetchall():
#         ls_tables.append(table[1])
#     if len(ls_tables) == 10:
#         pass
#     else:
#         __create_table__(conn)
#     return ls_tables


# def __create_table__(conn):
#     conn.execute('''CREATE TABLE if not exists Tabs (tab_id, position)''')
#     conn.execute('''CREATE TABLE if not exists Database (day_of_week_id, date_id, task_id, duration_id, starttime_id)''')
#     conn.execute('''CREATE TABLE if not exists MainDailyGroups (dailygroup_id, task_id)''')
#     conn.execute('''CREATE TABLE if not exists Projects (project_id, task_id)''')
#     conn.execute('''CREATE TABLE if not exists Days_task_active (task_id, days_task_active_id)''')
#     conn.execute('''CREATE TABLE if not exists MinDailyTaskDuration (task_id, min_duration_id)''')
#     conn.execute('''CREATE TABLE if not exists Date_deadline (task_id, date_id)''')
#     conn.execute('''CREATE TABLE if not exists PausedTasks (dailygroup_id, task_id)''')
#     conn.execute('''CREATE TABLE if not exists ArchivedTasks (dailygroup_id, task_id)''')
#     conn.execute('''CREATE TABLE if not exists Dailydatabase (day_of_week_id, date_id, task_id, duration_id)''')
#     conn.execute('''CREATE TABLE if not exists DailyStartTime (date_id, task_id, starttime_id)''')
#     conn.execute('''CREATE TABLE if not exists MainDailyGroups_bg_color (dailygroup_id, color_id)''')
#     if conn.execute('''select count(*) from Tabs ''').fetchone()[0] == 0:
#         print('len Tabs is zero, creating tab')
#         conn.execute('''INSERT INTO Tabs VALUES(?,?)''', ['tab','0'])
#     conn.commit()
