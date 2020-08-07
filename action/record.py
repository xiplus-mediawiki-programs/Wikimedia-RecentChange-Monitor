import json
import traceback

import pymysql

from record_config import recordwiki


def main(M, change):
    try:
        if change['type'] == 'abuselog':
            return

        wiki = change["wiki"]

        if wiki not in recordwiki:
            return

        M.change_wiki_and_domain(change['wiki'], change["meta"]["domain"])

        M.addRC_wiki(change)

        ctype = change["type"]

        unknowntype = True

        if ctype == "edit":
            M.addRC_edit(change)
            unknowntype = False

        elif ctype == "new":
            M.addRC_new(change)
            unknowntype = False

        elif ctype == "142":
            M.addRC_142(change)
            unknowntype = False

        elif ctype == "categorize":
            M.addRC_categorize(change)
            unknowntype = False

        elif ctype == "log":
            log_type = change["log_type"]
            log_action = change["log_action"]

            if log_type == "move":
                M.addRC_log_move(change)
                unknowntype = False

            elif log_type == "block":
                if log_action == "unblock":
                    M.addRC_log_block_unblock(change)
                    unknowntype = False

                elif log_action in ["block", "reblock"]:
                    M.addRC_log_block(change)
                    unknowntype = False

            elif log_type == "protect":
                if log_action == "unprotect":
                    M.addRC_log_protect_unprotect(change)
                    unknowntype = False

                elif log_action == "move_prot":
                    M.addRC_log_protect_move_prot(change)
                    unknowntype = False

                elif log_action in ["protect", "modify"]:
                    M.addRC_log_protect(change)
                    unknowntype = False

            elif log_type == "newusers":
                M.addRC_log_newusers(change)
                unknowntype = False

            elif log_type == "thanks":
                M.addRC_log_thanks(change)
                unknowntype = False

            elif log_type == "patrol":
                M.addRC_log_patrol(change)
                unknowntype = False

            elif log_type == "upload":
                M.addRC_log_upload(change)
                unknowntype = False

            elif log_type == "rights":
                M.addRC_log_rights(change)
                unknowntype = False

            elif log_type == "renameuser":
                M.addRC_log_renameuser(change)
                unknowntype = False

            elif log_type == "merge":
                M.addRC_log_merge(change)
                unknowntype = False

            elif log_type == "delete":
                if log_action == "delete":
                    M.addRC_log_delete(change)
                    unknowntype = False

                elif log_action == "delete_redir":
                    M.addRC_log_delete(change)
                    unknowntype = False

                elif log_action == "restore":
                    M.addRC_log_delete_restore(change)
                    unknowntype = False

                elif log_action == "revision":
                    M.addRC_log_delete_revision(change)
                    unknowntype = False

            elif log_type == "abusefilter":
                if log_action == "hit":
                    # Skip. Use abuselog.
                    unknowntype = False

                elif log_action in ["modify", "create"]:
                    M.addRC_log_abusefilter_modify(change)
                    unknowntype = False

            elif log_type == "globalauth":
                if log_action == "setstatus":
                    M.addRC_log_globalauth(change)
                    unknowntype = False

            elif log_type == "gblblock":
                if log_action in ["gblock2", "modify"]:
                    M.addRC_log_gblblock(change)
                    unknowntype = False

            elif log_type == "gblrename":
                if log_action == "rename":
                    M.addRC_log_gblrename(change)
                    unknowntype = False

            elif log_type == "gblrights":
                if log_action == "usergroups":
                    # ignore
                    unknowntype = False

            elif log_type == "pagetranslation":
                if log_action == "associate":
                    # ignore
                    unknowntype = False

                elif log_action == "mark":
                    # ignore
                    unknowntype = False

                elif log_action == "deletelok":
                    # ignore
                    unknowntype = False

                elif log_action == "prioritylanguages":
                    # ignore
                    unknowntype = False

            elif log_type == "translationreview":
                if log_action == "group":
                    # ignore
                    unknowntype = False

                elif log_action == "message":
                    # ignore
                    unknowntype = False

            elif log_type == "review":
                if log_action == "approve-i":
                    # ignore
                    unknowntype = False

                elif log_action == "approve":
                    # ignore
                    unknowntype = False

                elif log_action == "unapprove":
                    # ignore
                    unknowntype = False

            elif log_type == "import":
                if log_action == "interwiki":
                    # ignore
                    unknowntype = False

            elif log_type == "tag":
                if log_action == "update":
                    # ignore
                    unknowntype = False

            elif log_type == "massmessage":
                if log_action == "send":
                    # ignore
                    unknowntype = False

                elif log_action == "skipoptout":
                    # ignore
                    unknowntype = False

        if unknowntype:
            M.log(json.dumps(
                change, ensure_ascii=False), logtype='record/unknowntype')

    except pymysql.err.IntegrityError as e:
        M.error(e)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
