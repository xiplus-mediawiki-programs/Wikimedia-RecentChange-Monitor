import traceback

from Monitor import Monitor


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
            .mode-watch {
                background: #ffa;
            }
            .mode-blacklist {
                background: #fcc;
            }
        </style>
        <table>
        <tr>
            <th>wiki</th>
            <th>id</th>
            <th>name</th>
            <th>mode</th>
        </tr>
        """
        M.cur.execute("""SELECT `af_id`, `af_name`, `mode`, `wiki` FROM `abusefilter` ORDER BY `wiki` ASC, `af_id` ASC""")
        rows = M.cur.fetchall()
        for row in rows:
            html += """
                <tr class="mode-{2}">
                    <td>{3}</td>
                    <td>{0}</td>
                    <td>{1}</td>
                    <td>{2}</td>
                </tr>
                """.format(row[0], row[1], row[2], row[3])
        html += '</table>'
        return html
    except Exception:
        M.error(traceback.format_exc())
        return "OK1"
