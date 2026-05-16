--
-- PostgreSQL database dump
--

\restrict aujGmfzHIZMKRgYp2MGZksmrhPgknhdXS8it9mj1Y2efPmUTuRgyRPpt2YVShZa

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.4 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: card_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.card_type AS ENUM (
    'Visa',
    'MasterCard',
    'AmericanExpress',
    'RuPay',
    'Other'
);


ALTER TYPE public.card_type OWNER TO postgres;

--
-- Name: transaction_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.transaction_type AS ENUM (
    'income',
    'expense'
);


ALTER TYPE public.transaction_type OWNER TO postgres;

--
-- Name: trigger_set_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trigger_set_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
      BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
      END;
      $$;


ALTER FUNCTION public.trigger_set_timestamp() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cards (
    id integer NOT NULL,
    user_id integer NOT NULL,
    card_name character varying(100) NOT NULL,
    card_number character varying(19) NOT NULL,
    card_type public.card_type NOT NULL,
    expiry_date date NOT NULL,
    bank_name character varying(100) NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cards OWNER TO postgres;

--
-- Name: cards_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cards_id_seq OWNER TO postgres;

--
-- Name: cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cards_id_seq OWNED BY public.cards.id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    card_id integer,
    icon character varying(100),
    type public.transaction_type NOT NULL,
    category character varying(100) NOT NULL,
    amount numeric(12,2) NOT NULL,
    date timestamp with time zone DEFAULT now() NOT NULL,
    description text DEFAULT ''::text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    cards text DEFAULT ''::text,
    CONSTRAINT transactions_amount_check CHECK ((amount > (0)::numeric))
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transactions_id_seq OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    profile_image_url text DEFAULT ''::text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: cards id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cards ALTER COLUMN id SET DEFAULT nextval('public.cards_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: cards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cards (id, user_id, card_name, card_number, card_type, expiry_date, bank_name, is_default, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transactions (id, user_id, card_id, icon, type, category, amount, date, description, created_at, updated_at, cards) FROM stdin;
1	3	\N	\N	income	ds	10000.00	2026-05-12 05:30:00+05:30	jbsdjhc bjbds cn sdb	2026-05-14 00:51:48.279603+05:30	2026-05-14 00:51:48.279603+05:30	
2	3	\N	\N	expense	vhj	1000.00	2026-05-07 05:30:00+05:30	mnschjs hcvhas nm hjsva 	2026-05-14 23:29:58.523367+05:30	2026-05-14 23:29:58.523367+05:30	
3	3	\N	\N	expense	s chs 	1300.00	2026-05-12 05:30:00+05:30	jndnsjn jdsbjchbcd s js	2026-05-14 23:35:45.838575+05:30	2026-05-14 23:35:45.838575+05:30	
4	3	\N	\N	income	bhjcbjshd	50000.00	2026-04-30 05:30:00+05:30		2026-05-14 23:45:32.780922+05:30	2026-05-14 23:45:32.780922+05:30	
5	2	\N		income	kjdcbs	10000.00	2026-05-13 05:30:00+05:30		2026-05-17 00:46:00.647693+05:30	2026-05-17 00:46:00.647693+05:30	jcsd
6	2	\N		expense	sdjkcbc	292.00	2026-05-06 05:30:00+05:30		2026-05-17 00:46:14.689653+05:30	2026-05-17 00:46:14.689653+05:30	jknsdnc
7	2	\N		income	jkbbscd	3999.00	2026-05-12 05:30:00+05:30		2026-05-17 01:52:07.674824+05:30	2026-05-17 01:52:07.674824+05:30	jdsb
8	2	\N		income	bdshc	200000.00	2026-05-13 05:30:00+05:30		2026-05-17 01:52:40.421659+05:30	2026-05-17 01:52:40.421659+05:30	dsd
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, full_name, email, password, profile_image_url, created_at, updated_at) FROM stdin;
1	Test User	testuser123@example.com	$2b$10$t5VPlQkh36qxnubIw632Be8yJl7Cqke04og9KVTFjVf1a829KGIau		2026-05-14 00:48:41.224658+05:30	2026-05-14 00:48:41.224658+05:30
2	Balpreet Singh 	balpreetsinghgill83@gmail.com	$2b$10$F7kiuGJeOdid6d2DtxL3W.yR4ANDtMSn5SN5yrm/gly9FZ99.zwDu		2026-05-14 00:49:25.985374+05:30	2026-05-14 00:49:25.985374+05:30
3	Balpreet Singh Gill	chatgptpro417@gmail.com	$2b$10$DGetMVz5HHEmw6De0ViunutxAV0R7ijer2pd/s2Y4w6L94zqOwHXG	https://res.cloudinary.com/dnswhemu9/image/upload/v1778700059/expense_tracker-profile_images/dsyd3gbrl1stjcvoxcsy.png	2026-05-14 00:51:00.056711+05:30	2026-05-14 00:51:00.056711+05:30
\.


--
-- Name: cards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cards_id_seq', 1, false);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transactions_id_seq', 8, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: cards cards_card_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cards
    ADD CONSTRAINT cards_card_number_key UNIQUE (card_number);


--
-- Name: cards cards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cards
    ADD CONSTRAINT cards_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_cards_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cards_user_id ON public.cards USING btree (user_id);


--
-- Name: idx_transactions_card_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_card_id ON public.transactions USING btree (card_id);


--
-- Name: idx_transactions_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_date ON public.transactions USING btree (date DESC);


--
-- Name: idx_transactions_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_type ON public.transactions USING btree (type);


--
-- Name: idx_transactions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_user_id ON public.transactions USING btree (user_id);


--
-- Name: unique_default_card_per_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_default_card_per_user ON public.cards USING btree (user_id) WHERE (is_default = true);


--
-- Name: cards set_timestamp_cards; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_timestamp_cards BEFORE UPDATE ON public.cards FOR EACH ROW EXECUTE FUNCTION public.trigger_set_timestamp();


--
-- Name: transactions set_timestamp_transactions; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_timestamp_transactions BEFORE UPDATE ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.trigger_set_timestamp();


--
-- Name: users set_timestamp_users; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_timestamp_users BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.trigger_set_timestamp();


--
-- Name: cards fk_cards_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cards
    ADD CONSTRAINT fk_cards_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: transactions fk_transactions_card; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT fk_transactions_card FOREIGN KEY (card_id) REFERENCES public.cards(id) ON DELETE SET NULL;


--
-- Name: transactions fk_transactions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict aujGmfzHIZMKRgYp2MGZksmrhPgknhdXS8it9mj1Y2efPmUTuRgyRPpt2YVShZa

