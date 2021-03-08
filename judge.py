import time
import os
import random
import filecmp


def excute_many(now, sqlcode):
    sqlcommamds = sqlcode.split(';')
    for command in sqlcommamds:
        # print("---------------")
        # print("---------------")
        # print("---------------")
        # print("---------------")
        # print("---------------")
        # print(command)
        # print("---------------")
        # print("---------------")
        # print("---------------")
        # print("---------------")
        # print("---------------")
        if command != '':
            now.execute(command)
            print(command)


def sql_judge_select(code, checker, table_create_sql, table_delete_sql, db, now, cur1, cur2):
    try:
        excute_many(now, table_create_sql)
        db.commit()
        cur1.execute(code)
        cur2.execute(checker)
        db.commit()

        res1 = cur1.fetchall()
        res2 = cur2.fetchall()
        # 获取时间戳
        ticks1 = int(time.time())
        ticks2 = int(time.time()) + 1

        curdir = os.path.dirname(os.path.realpath(__file__)) + '/'
        file1 = curdir + str(ticks1) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.txt'
        file2 = curdir + str(ticks2) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.txt'

        # 将所得的数据存储为txt文件
        with open(file1, 'w') as fp:
            fp.write(str(res1))
        with open(file2, 'w') as fp:
            fp.write(str(res2))

        result = str(filecmp.cmp(file1, file2))
        os.remove(file1)
        os.remove(file2)
        excute_many(now, table_delete_sql)
        db.commit()

    except Exception as e:
        result = str(e)
    finally:
        return result


def sql_judge_update(code, checker, table_create_sql, table_delete_sql, table_select_sql, db, now, cur1, cur2):
    try:
        excute_many(now, table_create_sql)
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

        # 获取时间戳
        ticks1 = int(time.time())
        ticks2 = int(time.time()) + 1

        curdir = os.path.dirname(os.path.realpath(__file__)) + '/'
        file1 = curdir + str(ticks1) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.txt'
        file2 = curdir + str(ticks2) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.txt'

        # 将所得的数据存储为txt文件
        with open(file1, 'w') as fp:
            fp.write(str(res1))
        with open(file2, 'w') as fp:
            fp.write(str(res2))

        result = str(filecmp.cmp(file1, file2))
        os.remove(file1)
        os.remove(file2)
    except Exception as e:
        result = str(e)
    finally:
        return result


def sql_judge_view(code, checker, table_create_sql, table_delete_sql, table_select_sql, view_delete_sql, db, now, cur1,
                   cur2):
    try:
        print(table_create_sql)
        print(table_delete_sql)
        print(code)
        print(checker)

        excute_many(now, table_create_sql)
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

        # 获取时间戳
        ticks1 = int(time.time())
        ticks2 = int(time.time()) + 1

        curdir = os.path.dirname(os.path.realpath(__file__)) + '/'
        file1 = curdir + str(ticks1) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.txt'
        file2 = curdir + str(ticks2) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.txt'

        # 将所得的数据存储为txt文件
        with open(file1, 'w') as fp:
            fp.write(str(res1))
        with open(file2, 'w') as fp:
            fp.write(str(res2))

        result = str(filecmp.cmp(file1, file2))
        os.remove(file1)
        os.remove(file2)
    except Exception as e:
        result = str(e)
    finally:
        return result