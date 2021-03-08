import traceback
import pymysql
import time
import random
import re

from cachelib import SimpleCache

from config import Verdict, TRACEBACK_LIMIT
from judge import sql_judge_select, sql_judge_update, sql_judge_view

cache = SimpleCache()


def reject_with_traceback():
    return {'status': 'reject', 'message': traceback.format_exc(TRACEBACK_LIMIT)}


def judge_handler(fingerprint, code, checker, cases, table, problem_type,):
    try:
        DB = pymysql.connect(host='localhost', port=3306, user='root', password='xxx824650123', charset='utf8')
        cursor = DB.cursor()
        database_name = 'luck' + str(int(time.time())) + str(random.randint(1, 100)) + str(random.randint(1, 100))
        sqlcode = "create database " + database_name + " default character set utf8;"
        cursor.execute(sqlcode)
        DB.commit()
        try:
            db = pymysql.connect(host='localhost', port=3306, user='root', password='xxx824650123', charset='utf8', database=database_name)
            now = db.cursor()
            cur1 = db.cursor(cursor=pymysql.cursors.DictCursor)
            cur2 = db.cursor(cursor=pymysql.cursors.DictCursor)
            detail = [] # 判题细节
            table_delete_sql = ''
            for con in table['table_to_delete']:
                table_delete_sql += 'drop table ' + con + ';'
            response = {'status': 'received', 'verdict': Verdict.JUDGING.value, 'detail': detail} #判题时请求的信息(不断更新)
            average_point = 100 / len(cases)
            flag = 0
            for index, case in enumerate(cases):
                result = ''
                if problem_type == '查询类':
                    result = sql_judge_select(code, checker, case, table_delete_sql, db, now, cur1, cur2)
                elif problem_type == '更新类':
                    table_select_sql = 'select * from ' + table['table_to_do'][0] + ';'
                    result = sql_judge_update(code, checker, case, table_delete_sql, table_select_sql, db, now, cur1, cur2)
                elif problem_type == '创建视图类':
                    view_to_select = re.findall(r'^create\s+view\s+(\S+)\s*', code, re.I)
                    if view_to_select and view_to_select[0] == table['table_to_do'][0]:
                        table_select_sql = 'select * from ' + table['table_to_do'][0] + ';'
                        view_delete_sql = 'drop view ' + table['table_to_do'][0] + ';'
                        result = sql_judge_view(code, checker, case, table_delete_sql, table_select_sql, view_delete_sql, db, now, cur1, cur2)
                    else:
                        break
                point = 0
                if result == 'True':
                    flag = 0
                    point = average_point
                elif result == 'False':
                    flag = 4
                else:
                    flag = 2
                    break
                case_result = dict()
                dic = {'verdict': flag, 'info': result, 'point': point}
                case_result.update(dic)
                detail.append(case_result)  #本条加进去
                cache.set(fingerprint, response, timeout=3600)
            # if flag == 2:
            #     response['verdict'] = 2
            # else:
            response['verdict'] = 0
            print('END END END END END END END END END ')
        except Exception as e:
            response['verdict'] = 0
            print(e)
        finally:
            now.close()
            cur1.close()
            cur2.close()
            db.close()
    except:
        response = reject_with_traceback()
    finally:
        sqlcode = "drop database " + database_name + ";"
        cursor.execute(sqlcode)
        DB.commit()
        cursor.close()
        DB.close()
        cache.set(fingerprint, response, timeout=3600)
    return response
