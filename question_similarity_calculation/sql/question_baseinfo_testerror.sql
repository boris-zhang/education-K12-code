CREATE TABLE `core`.`question_baseinfo_testerror` (
  `question_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '题目标识',
  `testpaper_id` int(11) NOT NULL COMMENT '试卷标识',
  `question_no` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '题目序号',
  `question_stem` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '题干',
  `question_options` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '选',
  `answer` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '答案',
  `analysis` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '解析',
  `difficulty` decimal(5,4) DEFAULT NULL COMMENT '难度',
  `scrore` smallint(2) DEFAULT NULL COMMENT '分值',

  `question_type_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '题型',
  `textbook_version_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '教材版本名称',
  `grade_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '年级名称',
  `volume_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '版本号',

  `unit_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '单元名称',
  `knowledge_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '知识点名称',
  `super_knowledge_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '上级知识点名称',
  `subject_type` varchar(20) DEFAULT NULL COMMENT '科目类型',

  `image_filename` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '图片文件名',
  `path_image_loaded` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '图像文件路径',
  `source_type` varchar(255) DEFAULT NULL COMMENT '来源类型',
  `load_time` timestamp NULL DEFAULT NULL COMMENT '加载时间',
  PRIMARY KEY (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into `core`.`question_baseinfo_testerror` (
testpaper_id
,question_no
,question_stem
,question_options
,score
,question_type_name
,textbook_version_name
,grade_name
,unit_name
,knowledge_name
,subject_type
,image_filename
,path_image_loaded
,source_type
,load_time
)
select
t1.testpaper_id
,t1.question_no
,t1.question_stem
,t1.question_options
,t1.score
,t1.question_type_name
,t2.textbook_version_name
,t2.grade_name
,t1.unit_name
,t1.knowledge_name
,t2.subject_type
,t1.image_filename
,t1.path_image_loaded
,t2.source_type
,current_timestamp()
from testpaper_question_error t1
inner join testpaper_baseinfo t2 on t1.testpaper_id=t2.testpaper_id;


