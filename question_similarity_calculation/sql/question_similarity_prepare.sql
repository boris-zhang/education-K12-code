CREATE TABLE `core`.`question_similarity_prepare` (
  `question_seqno` int(11) NOT NULL AUTO_INCREMENT COMMENT '题目流水号',
  `in_tablename` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '所属表名',
  `question_ids` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci  NOT NULL COMMENT '题目标识',
  `question_num` smallint(2) NOT NULL COMMENT '题目数量',
  `question_stem` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '题干',
  `question_stem_segment` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '题干分词',
  `is_segmented` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否分词',
  `avg_difficulty` decimal(5,4) DEFAULT NULL COMMENT '平均难度',
  `question_type_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '题型',
  `grade_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '年级名称',
  `knowledge_names` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '知识点名称',
  `source_types` varchar(255) DEFAULT NULL COMMENT '来源类型',
  `subject_type` varchar(20) DEFAULT NULL COMMENT '科目类型',
  `load_time` timestamp NULL DEFAULT NULL COMMENT '加载时间',
  PRIMARY KEY (question_seqno)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into `core`.`question_similarity_prepare` (
in_tablename
,question_ids
,question_num
,question_stem
,is_segmented
,avg_difficulty
,question_type_name
,grade_name
,knowledge_names
,source_types
,subject_type
,load_time
)
select
'question_baseinfo_testerror'
,group_concat(distinct question_id)
,count(*)
,question_stem
,0
,avg(difficulty)
,question_type_name
,grade_name
,group_concat(distinct knowledge_name)
,group_concat(distinct source_type)
,subject_type
,current_timestamp()
from question_baseinfo_testerror
group by question_stem,question_type_name,grade_name,subject_type;

insert into `core`.`question_similarity_prepare` (
in_tablename
,question_ids
,question_num
,question_stem
,is_segmented
,avg_difficulty
,question_type_name
,grade_name
,knowledge_names
,source_types
,subject_type
,load_time
)
select
'question_baseinfo_crawler'
,group_concat(distinct question_id)
,count(*)
,question_stem
,0
,avg(difficulty)
,question_type_name
,grade_name
,group_concat(distinct knowledge_name)
,group_concat(distinct source_type)
,subject_type
,current_timestamp()
from question_baseinfo_crawler
group by question_stem,question_type_name,grade_name,subject_type;


