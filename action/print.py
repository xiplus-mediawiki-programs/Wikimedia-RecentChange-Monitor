import traceback
import logging

from print_config import followwiki


def main(M, change):
    try:
        if change['type'] == 'abuselog':
            return

        M.change_wiki_and_domain(change['wiki'], change["meta"]["domain"])

        wiki = change["wiki"]
        ctype = change["type"]
        user = change["user"]
        title = change["title"]
        comment = change["comment"]

        if change["bot"]:
            return

        if wiki not in followwiki:
            return

        if ctype == "edit":
            logging.info(user + " edit " + title)

        elif ctype == "new":
            logging.info(user + " create " + title)

        elif ctype == "142":
            pass

        elif ctype == "categorize":
            logging.info(user + " categorize " + title)

        elif ctype == "log":
            log_type = change["log_type"]
            log_action = change["log_action"]

            if log_type == "move":
                pass

            elif log_type == "block":
                logging.info("{} {} {} comment:{}".format(
                    user, log_action, title, change["log_action_comment"])
                )

                if log_action == "unblock":
                    pass

                elif log_action in ["block", "reblock"]:
                    pass

            elif log_type == "protect":
                if log_action == "unprotect":
                    logging.info(user + " unprotect " + title + " comment:" + comment)

                elif log_action == "move_prot":
                    logging.info(user + " move_prot " + title + " comment:" + comment)

                elif log_action in ["protect", "modify"]:
                    logging.info(user + " protect " + title + " comment:" + comment)

            elif log_type == "newusers":
                logging.info(user + " newusers " + title)

            elif log_type == "thanks":
                pass

            elif log_type == "patrol":
                pass

            elif log_type == "upload":
                pass

            elif log_type == "rights":
                pass

            elif log_type == "renameuser":
                pass

            elif log_type == "merge":
                pass

            elif log_type == "delete":
                if log_action == "delete":
                    pass

                elif log_action == "delete_redir":
                    pass

                elif log_action == "restore":
                    pass

                elif log_action == "revision":
                    pass

            elif log_type == "abusefilter":
                if log_action == "hit":
                    logging.info("{} hit af {} in {}".format(
                        user, change["log_params"]["filter"], title)
                    )

                elif log_action in ["modify", "create"]:
                    pass

            elif log_type == "globalauth":
                if log_action == "setstatus":
                    pass

            elif log_type == "gblblock":
                if log_action in ["gblock2", "modify"]:
                    pass

            elif log_type == "gblrename":
                if log_action == "rename":
                    pass

            elif log_type == "gblrights":
                if log_action == "usergroups":
                    pass

            elif log_type == "pagetranslation":
                if log_action == "associate":
                    pass

                elif log_action == "mark":
                    pass

                elif log_action == "deletelok":
                    pass

            elif log_type == "translationreview":
                if log_action == "group":
                    pass

                elif log_action == "message":
                    pass

            elif log_type == "review":
                if log_action == "approve-i":
                    pass

                elif log_action == "approve":
                    pass

                elif log_action == "unapprove":
                    pass

            elif log_type == "import":
                if log_action == "interwiki":
                    pass

            elif log_type == "tag":
                if log_action == "update":
                    pass

            elif log_type == "massmessage":
                if log_action == "send":
                    pass

                elif log_action == "skipoptout":
                    pass

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
