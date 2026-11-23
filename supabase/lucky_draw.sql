-- $100 Lucky Draw at 50,000 members (gamerbhai.com)
-- A "member" = a player with at least one server-verified Neon Run score.

-- 1) Public counter used by the progress bar (already installed 2026-11-23)
create or replace function public.get_member_count()
returns bigint
language sql security definer set search_path = public stable
as $$ select count(distinct user_id) from scores; $$;
revoke all on function public.get_member_count() from public;
grant execute on function public.get_member_count() to anon, authenticated;

-- 2) WHEN THE COUNTER REACHES 50,000: run this ONCE in the Supabase SQL editor
--    (screen-record it for transparency). It picks one member at random.
--    The ticket shown on the site is the first 8 characters of the player's id, upper-case.
-- select upper(left(user_id::text, 8)) as winning_ticket, max(name) as racer_name
-- from scores
-- group by user_id
-- order by random()
-- limit 1;
