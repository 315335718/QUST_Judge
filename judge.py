import time
import os
import random
import filecmp


def excute_many(now, sqlcode):
    sql_commands = sqlcode.split(';')
    for command in sql_commands:
        if command != '' and not command.isspace():
            command += ';'
            now.execute(command)


def sql_judge_select(code, checker, table_create_sql, table_delete_sql, db, now, cur1, cur2):
    try:
        excute_many(now, table_create_sql)
        db.commit()
        result = ''
        try:
            cur1.execute(code)
            cur2.execute(checker)
            db.commit()

            res1 = cur1.fetchall()
            res2 = cur2.fetchall()

            excute_many(now, table_delete_sql)
            db.commit()

            res1 = str(res1)
            res2 = str(res2)
            if res1 == res2:
                result = 'True'
            else:
                result = 'False'
        except Exception as e:
            result = 'CompileError' + ': ' + str(e)
    except Exception as e:
        result = 'SystemError' + ': ' + str(e)
    finally:
        return result


def sql_judge_update(code, checker, table_create_sql, table_delete_sql, table_select_sql, db, now, cur1, cur2):
    try:
        excute_many(now, table_create_sql)
        db.commit()
        result = ''
        try:
            cur1.execute(code)
            cur1.execute(table_select_sql)
            db.commit()
            res1 = cur1.fetchall()
            excute_many(now, table_delete_sql)
            db.commit()

            excute_many(now, table_create_sql)
            cur2.execute(checker)
            cur2.execute(table_select_sql)
            db.commit()
            res2 = cur2.fetchall()
            excute_many(now, table_delete_sql)
            db.commit()

            res1 = str(res1)
            res2 = str(res2)
            if res1 == res2:
                result = 'True'
            else:
                result = 'False'
        except Exception as e:
            result = 'CompileError' + ': ' + str(e)
    except Exception as e:
        result = 'SystemError' + ': ' + str(e)
    finally:
        return result


def sql_judge_view(code, checker, table_create_sql, table_delete_sql, table_select_sql, view_delete_sql, db, now, cur1,
                   cur2):
    try:
        excute_many(now, table_create_sql)
        db.commit()
        result = ''
        try:
            cur1.execute(code)
            cur1.execute(table_select_sql)
            db.commit()
            res1 = cur1.fetchall()
            cur1.execute(view_delete_sql)
            excute_many(now, table_delete_sql)
            db.commit()

            excute_many(now, table_create_sql)
            cur2.execute(checker)
            cur2.execute(table_select_sql)
            db.commit()
            res2 = cur2.fetchall()
            cur2.execute(view_delete_sql)
            excute_many(now, table_delete_sql)
            db.commit()

            res1 = str(res1)
            res2 = str(res2)
            if res1 == res2:
                result = 'True'
            else:
                result = 'False'
        except Exception as e:
            result = 'CompileError' + ': ' + str(e)
    except Exception as e:
        result = 'SystemError' + ': ' + str(e)
    finally:
        return result


def sql_judge_create(code, checker, insert_sql, table_delete_sql, db, now):
    try:
        excute_many(now, checker)
        db.commit()
        result = ''
        try:
            checker_states = []
            sql_commands = insert_sql.split(';')
            for command in sql_commands:
                if command != '' and not command.isspace():
                    try:
                        now.execute(command)
                        db.commit()
                        checker_states.append(1)
                    except Exception as e:
                        checker_states.append(0)
            excute_many(now, table_delete_sql)
            db.commit()

            excute_many(now, code)
            db.commit()
            code_states = []
            for command in sql_commands:
                if command != '' and not command.isspace():
                    try:
                        now.execute(command)
                        db.commit()
                        code_states.append(1)
                    except Exception as e:
                        code_states.append(0)
            excute_many(now, table_delete_sql)
            db.commit()

            flag = 1
            for index, state in enumerate(checker_states):
                if state != code_states[index]:
                    flag = 0
                    break
            if flag == 1:
                result = 'True'
            else:
                result = 'False'
        except Exception as e:
            result = 'CompileError' + ': ' + str(e)
    except Exception as e:
        result = 'SystemError' + ': ' + str(e)
    finally:
        return result