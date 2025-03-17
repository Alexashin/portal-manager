-- Adminer 4.8.1 PostgreSQL 17.2 (Debian 17.2-1.pgdg120+1) dump

\connect "portal_db";

CREATE TABLE "public"."bot_settings" (
    "key" text NOT NULL,
    "value" text NOT NULL,
    CONSTRAINT "bot_settings_pkey" PRIMARY KEY ("key")
) WITH (oids = false);


CREATE SEQUENCE final_exam_answers_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."final_exam_answers" (
    "id" integer DEFAULT nextval('final_exam_answers_id_seq') NOT NULL,
    "user_id" bigint NOT NULL,
    "question_id" integer NOT NULL,
    "chosen_option" integer,
    "open_answer" text,
    "is_correct" boolean,
    "attempt_number" integer DEFAULT '1',
    "timestamp" timestamp DEFAULT now(),
    CONSTRAINT "final_exam_answers_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE final_exam_questions_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."final_exam_questions" (
    "id" integer DEFAULT nextval('final_exam_questions_id_seq') NOT NULL,
    "question" text NOT NULL,
    "is_open_question" boolean DEFAULT false,
    "option_1" text,
    "option_2" text,
    "option_3" text,
    "option_4" text,
    "correct_option" integer,
    CONSTRAINT "final_exam_questions_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE final_exam_results_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."final_exam_results" (
    "id" integer DEFAULT nextval('final_exam_results_id_seq') NOT NULL,
    "user_id" bigint NOT NULL,
    "total_questions" integer NOT NULL,
    "correct_answers" integer NOT NULL,
    "passed" boolean DEFAULT false,
    "exam_date" timestamp DEFAULT now(),
    "attempt_number" integer DEFAULT '1',
    "attempt_date" timestamp DEFAULT now(),
    CONSTRAINT "final_exam_results_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE lessons_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."lessons" (
    "id" integer DEFAULT nextval('lessons_id_seq') NOT NULL,
    "module_id" integer,
    "title" text NOT NULL,
    "content" text,
    "file_ids" text[],
    "video_ids" text[],
    "lesson_order" integer NOT NULL,
    "created_at" timestamp DEFAULT now(),
    CONSTRAINT "lessons_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE modules_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."modules" (
    "id" integer DEFAULT nextval('modules_id_seq') NOT NULL,
    "title" text NOT NULL,
    "description" text,
    "created_at" timestamp DEFAULT now(),
    CONSTRAINT "modules_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE roles_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."roles" (
    "id" integer DEFAULT nextval('roles_id_seq') NOT NULL,
    "name" character varying(50) NOT NULL,
    CONSTRAINT "roles_name_key" UNIQUE ("name"),
    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE tests_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."tests" (
    "id" integer DEFAULT nextval('tests_id_seq') NOT NULL,
    "module_id" integer NOT NULL,
    "question" text NOT NULL,
    "option_1" text NOT NULL,
    "option_2" text NOT NULL,
    "option_3" text NOT NULL,
    "option_4" text NOT NULL,
    "correct_option" integer NOT NULL,
    CONSTRAINT "tests_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


CREATE SEQUENCE user_module_progress_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."user_module_progress" (
    "id" integer DEFAULT nextval('user_module_progress_id_seq') NOT NULL,
    "user_id" bigint NOT NULL,
    "module_id" integer NOT NULL,
    "is_completed" boolean DEFAULT false,
    "can_access" boolean DEFAULT false,
    "last_attempt" timestamp DEFAULT now(),
    CONSTRAINT "unique_user_module" UNIQUE ("user_id", "module_id"),
    CONSTRAINT "user_module_progress_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "user_module_progress_user_id_module_id_key" UNIQUE ("user_id", "module_id")
) WITH (oids = false);


CREATE TABLE "public"."users" (
    "tg_id" bigint NOT NULL,
    "role_id" integer NOT NULL,
    "full_name" text,
    "created_at" timestamp DEFAULT now(),
    CONSTRAINT "users_pkey" PRIMARY KEY ("tg_id")
) WITH (oids = false);


ALTER TABLE ONLY "public"."final_exam_answers" ADD CONSTRAINT "final_exam_answers_question_id_fkey" FOREIGN KEY (question_id) REFERENCES final_exam_questions(id) ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."final_exam_answers" ADD CONSTRAINT "final_exam_answers_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(tg_id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."final_exam_results" ADD CONSTRAINT "final_exam_results_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(tg_id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."lessons" ADD CONSTRAINT "lessons_module_id_fkey" FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."tests" ADD CONSTRAINT "tests_module_id_fkey" FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."user_module_progress" ADD CONSTRAINT "user_module_progress_module_id_fkey" FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."user_module_progress" ADD CONSTRAINT "user_module_progress_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(tg_id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."users" ADD CONSTRAINT "users_role_id_fkey" FOREIGN KEY (role_id) REFERENCES roles(id) NOT DEFERRABLE;

-- 2025-03-17 15:31:46.096155+03
