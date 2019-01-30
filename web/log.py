import cgi
import traceback

import pymysql
from flask import make_response, render_template, request

from Monitor import Monitor
from tables import tables


def web():
    M = Monitor()
    try:
        html = """
            <a href="./status">status</a>
            log
            <a href="./blacklist">blacklist</a>
            <form>
            """
        for table in tables:
            html += ('<button type="submit" name="type" value="{0}">' +
                     '{0}</button> ').format(table)
        html += '</form>'
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
                    html += 'No record'
                else:
                    html += """
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
                    html += '<table>'
                    html += '<tr>'
                    for col in rows[0]:
                        if col == "parsedcomment":
                            continue
                        html += '<th>' + col + '</th>'
                    html += '</tr>'
                    for row in rows:
                        html += '<tr>'
                        for col in row:
                            if col == "parsedcomment":
                                continue
                            elif (logtype == "error" and col == "error"):
                                html += ('<td><pre>' +
                                         cgi.escape(row[col], quote=False) +
                                         '</pre></td>')
                            elif (col == "log_action_comment"
                                  or col == "comment"):
                                html += ('<td>' +
                                         cgi.escape(row[col], quote=False) +
                                         '</pre>')
                            elif col == "timestamp":
                                html += '<td>{} ({})</td>'.format(str(row[col]), M.formattimediff(row[col]))
                            else:
                                html += '<td>' + str(row[col]) + '</td>'
                        html += '</tr>'
                    html += '</table>'
        return html
    except Exception:
        M.error(traceback.format_exc())
        return traceback.format_exc()
