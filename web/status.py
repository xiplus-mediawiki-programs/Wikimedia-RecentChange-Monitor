import traceback

from Monitor import Monitor
from tables import tables


def web():
    M = Monitor()
    try:
        html = """
        <style>
            table {
                border-collapse: collapse;
            }
            th, td {
                vertical-align: top;
                border: 1px solid black;
            }
        </style>
        status
        <a href="./log?type=log">log</a>
        <a href="./blacklist">blacklist</a>
        <table>
        <tr>
            <th>database</th>
            <th>last time</th>
        </tr>
        """
        for table in tables:
            M.cur.execute("""SELECT MAX(`timestamp`) FROM """ + table)
            rows = M.cur.fetchall()
            if rows[0][0] is None:
                html += """
                    <tr>
                        <td>{}</td>
                        <td>No record</td>
                    </tr>
                    """.format(table)
            else:
                html += """
                    <tr>
                        <td><a href="{0}log?type={1}" target="_blank">{1}</td>
                        <td>{2}</td>
                    </tr>
                    """.format(M.siteurl, table, M.formattimediff(rows[0][0]))
        html += '</table>'
        return html
    except Exception:
        M.error(traceback.format_exc())
        return "OK1"
