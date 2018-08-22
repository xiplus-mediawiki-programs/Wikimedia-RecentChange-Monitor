SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `admin` (
  `user_id` int(11) NOT NULL,
  `name` varchar(255) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `black_ipv4` (
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `val` varchar(255) NOT NULL,
  `userhash` bigint(20) NOT NULL,
  `start` decimal(10,0) NOT NULL,
  `end` decimal(10,0) NOT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `black_ipv6` (
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `val` varchar(255) NOT NULL,
  `userhash` bigint(20) NOT NULL,
  `start` decimal(39,0) NOT NULL,
  `end` decimal(39,0) NOT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `black_page` (
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `page` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `black_user` (
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `userhash` bigint(20) NOT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `bot_message` (
  `timestamp` int(11) NOT NULL,
  `message_id` int(11) NOT NULL,
  `user` varchar(255) COLLATE utf8_bin NOT NULL,
  `page` varchar(255) COLLATE utf8_bin NOT NULL,
  `message` text COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `error` (
  `timestamp` int(11) NOT NULL,
  `error` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `autotime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `log` (
  `timestamp` int(11) NOT NULL,
  `type` varchar(20) NOT NULL DEFAULT '',
  `log` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `autotime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_142` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_categorize` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_edit` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `length_new` int(11) NOT NULL,
  `length_old` int(11) NOT NULL,
  `minor` tinyint(1) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `revision_new` int(11) NOT NULL,
  `revision_old` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_abusefilter_hit` (
  `bot` tinyint(1) NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_action` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_actions` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_filter` int(11) NOT NULL,
  `log_params_log` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_abusefilter_modify` (
  `bot` tinyint(1) NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_historyId` int(11) NOT NULL,
  `log_params_newId` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_abuselog` (
  `id` int(11) NOT NULL,
  `filter_id` int(11) NOT NULL,
  `filter` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `ns` int(11) NOT NULL,
  `revid` int(11) NOT NULL,
  `result` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_block` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_flags` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_duration` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_delete` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_delete_restore` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_count_files` int(11) NOT NULL,
  `log_params_count_revisions` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_delete_revision` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_ids` text CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_type` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_nfield` int(11) NOT NULL,
  `log_params_ofield` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_gblblock` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_gblrename` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_movepages` tinyint(1) NOT NULL,
  `log_params_suppressredirects` tinyint(1) NOT NULL,
  `log_params_olduser` varchar(255) COLLATE utf8_bin NOT NULL,
  `log_params_newuser` varchar(255) COLLATE utf8_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `RC_log_globalauth` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_merge` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_dest` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_params_mergepoint` bigint(20) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_move` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_noredir` tinyint(1) NOT NULL,
  `log_params_target` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_newusers` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_userid` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_patrol` (
  `bot` tinyint(1) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_auto` tinyint(1) NOT NULL,
  `log_params_previd` int(11) NOT NULL,
  `log_params_curid` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_protect` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_details` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_params_cascade` tinyint(1) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_protect_move_prot` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_oldtitle` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_protect_unprotect` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_renameuser` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_olduser` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_params_newuser` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_params_edits` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_rights` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_newgroups` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_oldgroups` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_newmetadata` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_params_oldmetadata` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_thanks` (
  `bot` tinyint(1) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `namespace` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_log_upload` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `log_action` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `log_action_comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `log_id` int(11) NOT NULL,
  `log_params_img_timestamp` bigint(20) NOT NULL,
  `log_params_img_sha1` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `RC_new` (
  `bot` tinyint(1) NOT NULL,
  `comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `id` int(11) NOT NULL,
  `length_new` int(11) NOT NULL,
  `minor` tinyint(1) NOT NULL,
  `namespace` int(11) NOT NULL,
  `parsedcomment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `patrolled` tinyint(1) NOT NULL,
  `revision_new` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `wiki` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `user_score` (
  `userhash` bigint(20) NOT NULL,
  `point` int(11) NOT NULL DEFAULT '0',
  `timestamp` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `white_user` (
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `userhash` bigint(20) NOT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `timestamp` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


ALTER TABLE `admin`
  ADD UNIQUE KEY `user_id` (`user_id`);

ALTER TABLE `user_score`
  ADD UNIQUE KEY `user` (`userhash`) USING BTREE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
