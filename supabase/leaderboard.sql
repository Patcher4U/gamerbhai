-- Neon Run leaderboard for ilovegta6 (run once in Supabase SQL editor)
-- Players sign in anonymously (no email needed) and pick a nickname.
-- Scores can only be written through submit_score(), which checks the run was really played.

create table if not exists public.runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  started_at timestamptz not null default now(),
  finished boolean not null default false
);

create table if not exists public.scores (
  id bigint generated always as identity primary key,
  user_id uuid not null,
  name text not null,
  score integer not null,
  coins integer not null default 0,
  near integer not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists scores_score_idx on public.scores (score desc);
create index if not exists scores_user_idx on public.scores (user_id);
create index if not exists runs_user_idx on public.runs (user_id, started_at desc);

-- lock tables: nobody reads/writes them directly, only through the functions below
alter table public.runs enable row level security;
alter table public.scores enable row level security;
revoke all on public.runs, public.scores from anon, authenticated;

-- 1) call when the countdown starts
create or replace function public.start_run()
returns uuid
language plpgsql security definer set search_path = public
as $$
declare uid uuid := auth.uid(); rid uuid;
begin
  if uid is null then raise exception 'not signed in'; end if;
  if exists (select 1 from runs where user_id = uid and started_at > now() - interval '3 seconds') then
    raise exception 'too fast';
  end if;
  insert into runs(user_id) values (uid) returning id into rid;
  return rid;
end $$;

-- 2) call after the crash
create or replace function public.submit_score(p_run uuid, p_name text, p_score int, p_coins int, p_near int)
returns integer   -- returns the player's global rank (1 = top)
language plpgsql security definer set search_path = public
as $$
declare uid uuid := auth.uid(); r runs; secs numeric; nm text; best int; rnk int;
begin
  if uid is null then raise exception 'not signed in'; end if;
  select * into r from runs where id = p_run and user_id = uid for update;
  if not found or r.finished then raise exception 'bad run'; end if;
  update runs set finished = true where id = p_run;
  secs := extract(epoch from now() - r.started_at);
  if secs < 3 or secs > 3600 then raise exception 'bad time'; end if;
  -- plausibility: top speed gives ~58 pts/sec, near miss = 50 each
  if p_score < 0 or p_coins < 0 or p_near < 0
     or p_near > secs * 1.5 or p_coins > secs * 1.5
     or p_score > secs * 62 + p_near * 50 then
    raise exception 'score rejected';
  end if;
  nm := btrim(regexp_replace(coalesce(p_name, ''), '[^A-Za-z0-9_ .\-]', '', 'g'));
  if length(nm) < 2 then nm := 'Player'; end if;
  nm := left(nm, 16);
  insert into scores(user_id, name, score, coins, near) values (uid, nm, p_score, p_coins, p_near);
  update scores set name = nm where user_id = uid;   -- keep one name per player
  select max(score) into best from scores where user_id = uid;
  select count(*) + 1 into rnk from (
    select user_id, max(score) s from scores group by user_id
  ) t where t.s > best;
  return rnk;
end $$;

-- 3) public top list (best score per player)
create or replace function public.get_leaderboard(p_limit int default 10)
returns table(rank bigint, name text, score int, me boolean)
language sql security definer set search_path = public stable
as $$
  select row_number() over (order by b.s desc, b.t asc) as rank, b.name, b.s, b.user_id = auth.uid()
  from (
    select distinct on (user_id) user_id, name, score s, created_at t
    from scores order by user_id, score desc, created_at asc
  ) b
  order by b.s desc, b.t asc
  limit least(greatest(p_limit, 1), 50);
$$;

revoke all on function public.start_run() from public;
revoke all on function public.submit_score(uuid, text, int, int, int) from public;
grant execute on function public.start_run() to authenticated;
grant execute on function public.submit_score(uuid, text, int, int, int) to authenticated;
grant execute on function public.get_leaderboard(int) to anon, authenticated;
