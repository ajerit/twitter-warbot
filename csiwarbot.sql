--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.13
-- Dumped by pg_dump version 11.3

-- Started on 2019-07-25 22:51:05

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE csiwarbot;
--
-- TOC entry 2135 (class 1262 OID 16385)
-- Name: csiwarbot; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE csiwarbot WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'es_ES.UTF-8' LC_CTYPE = 'es_ES.UTF-8';


ALTER DATABASE csiwarbot OWNER TO postgres;

\connect csiwarbot

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 186 (class 1259 OID 16388)
-- Name: players; Type: TABLE; Schema: public; Owner: pi
--

CREATE TABLE public.players (
    id integer NOT NULL,
    name text NOT NULL,
    isalive boolean DEFAULT true NOT NULL,
    deathprob integer DEFAULT 100 NOT NULL,
    selectprob integer DEFAULT 10 NOT NULL,
    wins smallint DEFAULT 0 NOT NULL
);


ALTER TABLE public.players OWNER TO pi;

--
-- TOC entry 185 (class 1259 OID 16386)
-- Name: players_id_seq; Type: SEQUENCE; Schema: public; Owner: pi
--

CREATE SEQUENCE public.players_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.players_id_seq OWNER TO pi;

--
-- TOC entry 2137 (class 0 OID 0)
-- Dependencies: 185
-- Name: players_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pi
--

ALTER SEQUENCE public.players_id_seq OWNED BY public.players.id;


--
-- TOC entry 2006 (class 2604 OID 16391)
-- Name: players id; Type: DEFAULT; Schema: public; Owner: pi
--

ALTER TABLE ONLY public.players ALTER COLUMN id SET DEFAULT nextval('public.players_id_seq'::regclass);


--
-- TOC entry 2012 (class 2606 OID 16400)
-- Name: players players_pkey; Type: CONSTRAINT; Schema: public; Owner: pi
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_pkey PRIMARY KEY (id);


--
-- TOC entry 2136 (class 0 OID 0)
-- Dependencies: 2135
-- Name: DATABASE csiwarbot; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON DATABASE csiwarbot TO pi;


-- Completed on 2019-07-25 22:51:06

--
-- PostgreSQL database dump complete
--

