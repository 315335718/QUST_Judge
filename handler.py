import traceback
import pymysql
import time
import random
import re

from cachelib import SimpleCache

from config import Verdict, TRACEBACK_LIMIT
from judge import sql_judge_select, sql_judge_update, sql_judge_view, sql_judge_create

cache = SimpleCache()


def reject_with_traceback():
    return {'status': 'reject', 'message': traceback.format_exc(TRACEBACK_LIMIT)}


def judge_handler(fingerprint, code, checker, cases, table, problem_type, ):
    try:
        DB = pymysql.connect(host='localhost', port=3306, user='root', password='xxx824650123', charset='utf8')
        cursor = DB.cursor()
        database_name = 'luck' + str(int(time.time())) + str(random.randint(1, 100)) + str(random.randint(1, 100))
        sqlcode = "create database " + database_name + " default character set utf8;"
        cursor.execute(sqlcode)
        DB.commit()
        try:
            db = pymysql.connect(host='localhost', port=3306, user='root', password='xxx824650123', charset='utf8',
                                 database=database_name)
            now = db.cursor()
            cur1 = db.cursor(cursor=pymysql.cursors.DictCursor)
            cur2 = db.cursor(cursor=pymysql.cursors.DictCursor)

            detail = []  # 判题细节
            response = {'status': 'received', 'verdict': Verdict.JUDGING.value, 'detail': detail}  # 判题时请求的信息(不断更新)
            flag = -1  # 判题结果标志
            table_delete_sql = ''
            table_select_sql = ''
            view_to_select = ''
            view_delete_sql = ''
            status_message = ''
            table['table_to_delete'].reverse()
            for con in table['table_to_delete']:
                table_delete_sql += 'drop table ' + con + ';'
            if problem_type == '更新类':
                table_select_sql = 'select * from ' + table['table_to_do'][0] + ';'
            elif problem_type == '创建视图类':
                view_to_select = re.findall(r'^create\s+view\s+(\S+)\s*', code, re.I)
                if view_to_select and view_to_select[0] == table['table_to_do'][0]:
                    view_delete_sql = 'drop view ' + table['table_to_do'][0] + ';'
                    table_select_sql = 'select * from ' + table['table_to_do'][0] + ';'
                else:
                    flag = 0  # 视图表名不正确，答案错误
                    case_result = dict()
                    dic = {'verdict': flag, 'point': 0}
                    status_message = '视图表名不正确，答案错误'
                    case_result.update(dic)
                    detail.append(case_result)  # 本条加进去
                    cache.set(fingerprint, response, timeout=3600)
            elif problem_type == '创建基本表':
                table_to_create = re.findall(r'\s*create\s+table\s+(\S+)\s*\(', code, re.I)
                set1 = set(table['table_to_do'])
                set2 = set(table_to_create)
                table_delete_sql = ''
                table_to_create.reverse()
                if table_to_create and ((set1 & set2) == (set1 | set2)):
                    for t in table_to_create:
                        table_delete_sql += 'drop table ' + t + ';'
                else:
                    flag = 0  # 基本表名不正确，答案错误
                    case_result = dict()
                    dic = {'verdict': flag, 'point': 0}
                    status_message = '基本表名不正确，答案错误'
                    case_result.update(dic)
                    detail.append(case_result)  # 本条加进去
                    cache.set(fingerprint, response, timeout=3600)

            cases_len = len(cases)
            if cases_len > 0 and flag == -1:
                average_point = 100 / len(cases)
                case = cases[0]
                pre = ''
                if problem_type == '查询类':
                    pre = sql_judge_select(code, checker, case, table_delete_sql, db, now, cur1, cur2)
                elif problem_type == '更新类':
                    pre = sql_judge_update(code, checker, case, table_delete_sql, table_select_sql, db, now, cur1,
                                           cur2)
                elif problem_type == '创建视图类':
                    pre = sql_judge_view(code, checker, case, table_delete_sql, table_select_sql, view_delete_sql,
                                         db, now, cur1, cur2)
                elif problem_type == '创建基本表':
                    pre = sql_judge_create(code, checker, case, table_delete_sql, db, now)
                if pre == 'True' or pre == 'False':
                    for index, case in enumerate(cases):
                        result = ''
                        if problem_type == '查询类':
                            result = sql_judge_select(code, checker, case, table_delete_sql, db, now, cur1, cur2)
                        elif problem_type == '更新类':
                            result = sql_judge_update(code, checker, case, table_delete_sql, table_select_sql, db, now,
                                                      cur1, cur2)
                        elif problem_type == '创建视图类':
                            result = sql_judge_view(code, checker, case, table_delete_sql, table_select_sql,
                                                    view_delete_sql, db, now, cur1, cur2)
                        elif problem_type == '创建基本表':
                            result = sql_judge_create(code, checker, case, table_delete_sql, db, now)

                        case_result = dict()
                        if result == 'True':
                            dic = {'verdict': 0, 'point': average_point}
                        else:
                            dic = {'verdict': 4, 'point': 0}
                        case_result.update(dic)
                        detail.append(case_result)  # 本条加进去
                        cache.set(fingerprint, response, timeout=3600)
                    flag = 0  # 评测完成
                    status_message = '正常评测'
                elif len(pre) >= 11 and pre[:11] == 'SystemError':
                    flag = 3  # 题目信息有误
                    case_result = dict()
                    dic = {'verdict': flag, 'point': 0}
                    status_message = '系统错误: 题目信息有误,' + pre
                    case_result.update(dic)
                    detail.append(case_result)  # 本条加进去
                    cache.set(fingerprint, response, timeout=3600)
                elif len(pre) >= 12 and pre[:12] == 'CompileError':
                    flag = 2  # 编译错误
                    case_result = dict()
                    dic = {'verdict': flag, 'point': 0}
                    status_message = '编译错误: ' + pre
                    case_result.update(dic)
                    detail.append(case_result)  # 本条加进去
                    cache.set(fingerprint, response, timeout=3600)
            elif flag != 0:
                flag = 3  # 没有测试点，系统错误
                case_result = dict()
                dic = {'verdict': flag, 'point': 0}
                status_message = '系统错误: 没有测试点'
                case_result.update(dic)
                detail.append(case_result)  # 本条加进去
                cache.set(fingerprint, response, timeout=3600)

            response['verdict'] = flag
            response['status_message'] = status_message
        except Exception as e:
            response['verdict'] = 3
            status_message = '系统错误: ' + e
            response['status_message'] = status_message
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
