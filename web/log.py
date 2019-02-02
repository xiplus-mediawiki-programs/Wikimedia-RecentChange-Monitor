import html
import traceback

import pymysql
from flask import request

from Monitor import Monitor
from tables import tables


def web():
    M = Monitor()
    try:
        result = """
            <a href="./status">status</a>
            log
            <a href="./blacklist">blacklist</a>
            <form>
            """
        for table in tables:
            result += ('<button type="submit" name="type" value="{0}">' +
                       '{0}</button> ').format(table)
        result += '</form>'
        if "type" in request.args:
            logtype = request.args["type"]
            if logtype in tables:
                M.cur2 = M.db.cursor(pymysql.cursors.DictCursor)
                M.cur2.execute(
                    """SELECT * FROM {} ORDER BY `timestamp` DESC LIMIT 20"""
                    .format(logtype)
                )
                rows = M.cur2.fetchall()
                if len(rows) == 0:
                    result += 'No record'
                else:
                    result += """
                        <style>
                        table {
                            border-collapse: collapse;
                        }
                        th, td {
                            vertical-align: top;
                            border: 1px solid black;
                        }
                        </style>
                        """
                    result += '<table>'
                    result += '<tr>'
                    for col in rows[0]:
                        if col == "parsedcomment":
                            continue
                        result += '<th>' + col + '</th>'
                    result += '</tr>'
                    for row in rows:
                        result += '<tr>'
                        for col in row:
                            if col == "parsedcomment":
                                continue
                            elif (logtype == "error" and col == "error"):
                                result += ('<td><pre>' +
                                           html.escape(row[col], quote=False) +
                                           '</pre></td>')
                            elif col in ['log_action_comment', 'comment']:
                                result += ('<td>' +
                                           html.escape(row[col], quote=False) +
                                           '</pre>')
                            elif col == "timestamp":
                                result += '<td>{} ({})</td>'.format(
                                    str(row[col]), M.formattimediff(row[col]))
                            else:
                                result += '<td>' + str(row[col]) + '</td>'
                        result += '</tr>'
                    result += '</table>'
        return result
    except Exception:
        M.error(traceback.format_exc())
        return traceback.format_exc()
