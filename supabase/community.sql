-- GamerBhai community: posts, comments, live chat, uploads with owner approval.
-- Text goes live at once (admin can delete). Posts with a file stay "pending" (only the uploader
-- and the admin can see them) until the admin approves.

create table if not exists public.admins (user_id uuid primary key references auth.users on delete cascade);
alter table public.admins enable row level security;   -- no policies: nobody can read/write it from the site

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as
$$ select exists (select 1 from public.admins where user_id = auth.uid()) $$;

create or replace function public.is_real_user() returns boolean
language sql stable as
$$ select auth.uid() is not null and coalesce((auth.jwt() ->> 'is_anonymous')::boolean, false) = false $$;

-- ---------- posts ----------
create table if not exists public.posts (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  author text not null check (char_length(author) between 2 and 16),
  body text not null check (char_length(body) between 1 and 2000),
  file_path text,
  file_type text,
  status text not null default 'pending' check (status in ('approved','pending','rejected')),
  created_at timestamptz not null default now()
);
create index if not exists posts_status_time on public.posts (status, created_at desc);

create or replace function public.posts_before_insert() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.user_id := auth.uid();
  new.created_at := now();
  if new.file_path is not null and split_part(new.file_path, '/', 1) <> auth.uid()::text then
    raise exception 'bad file path';
  end if;
  new.status := case when new.file_path is null or public.is_admin() then 'approved' else 'pending' end;
  if not public.is_admin() and (select count(*) from public.posts where user_id = auth.uid() and created_at > now() - interval '10 minutes') >= 5 then
    raise exception 'Slow down: max 5 posts per 10 minutes';
  end if;
  return new;
end $$;
drop trigger if exists posts_bi on public.posts;
create trigger posts_bi before insert on public.posts for each row execute function public.posts_before_insert();

alter table public.posts enable row level security;
drop policy if exists posts_read on public.posts;
create policy posts_read on public.posts for select using (status = 'approved' or user_id = auth.uid() or public.is_admin());
drop policy if exists posts_add on public.posts;
create policy posts_add on public.posts for insert to authenticated with check (public.is_real_user());
drop policy if exists posts_mod on public.posts;
create policy posts_mod on public.posts for update to authenticated using (public.is_admin()) with check (public.is_admin());
drop policy if exists posts_del on public.posts;
create policy posts_del on public.posts for delete to authenticated using (user_id = auth.uid() or public.is_admin());

-- ---------- comments ----------
create table if not exists public.comments (
  id bigint generated always as identity primary key,
  post_id bigint not null references public.posts on delete cascade,
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  author text not null check (char_length(author) between 2 and 16),
  body text not null check (char_length(body) between 1 and 500),
  created_at timestamptz not null default now()
);
create index if not exists comments_post on public.comments (post_id, created_at);

create or replace function public.comments_before_insert() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.user_id := auth.uid(); new.created_at := now();
  if not public.is_admin() and (select count(*) from public.comments where user_id = auth.uid() and created_at > now() - interval '5 minutes') >= 10 then
    raise exception 'Slow down: max 10 comments per 5 minutes';
  end if;
  return new;
end $$;
drop trigger if exists comments_bi on public.comments;
create trigger comments_bi before insert on public.comments for each row execute function public.comments_before_insert();

alter table public.comments enable row level security;
drop policy if exists comments_read on public.comments;
create policy comments_read on public.comments for select using (exists (select 1 from public.posts p where p.id = post_id));
drop policy if exists comments_add on public.comments;
create policy comments_add on public.comments for insert to authenticated with check (auth.uid() is not null and exists (select 1 from public.posts p where p.id = post_id and p.status = 'approved'));
drop policy if exists comments_del on public.comments;
create policy comments_del on public.comments for delete to authenticated using (user_id = auth.uid() or public.is_admin());

-- ---------- live chat ----------
create table if not exists public.chat (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  author text not null check (char_length(author) between 2 and 16),
  body text not null check (char_length(body) between 1 and 300),
  created_at timestamptz not null default now()
);
create index if not exists chat_time on public.chat (created_at desc);

create or replace function public.chat_before_insert() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.user_id := auth.uid(); new.created_at := now();
  if not public.is_admin() and exists (select 1 from public.chat where user_id = auth.uid() and created_at > now() - interval '3 seconds') then
    raise exception 'Slow down: one message every 3 seconds';
  end if;
  return new;
end $$;
drop trigger if exists chat_bi on public.chat;
create trigger chat_bi before insert on public.chat for each row execute function public.chat_before_insert();

alter table public.chat enable row level security;
drop policy if exists chat_read on public.chat;
create policy chat_read on public.chat for select using (true);
drop policy if exists chat_add on public.chat;
create policy chat_add on public.chat for insert to authenticated with check (auth.uid() is not null);
drop policy if exists chat_del on public.chat;
create policy chat_del on public.chat for delete to authenticated using (user_id = auth.uid() or public.is_admin());

grant select on public.posts, public.comments, public.chat to anon, authenticated;
grant insert, delete on public.posts, public.comments, public.chat to authenticated;
grant update (status) on public.posts to authenticated;
grant execute on function public.is_admin() to anon, authenticated;

-- ---------- uploads (private bucket, 5 MB images) ----------
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('community', 'community', false, 5242880, array['image/jpeg','image/png','image/webp','image/gif'])
on conflict (id) do update set public = false, file_size_limit = 5242880, allowed_mime_types = array['image/jpeg','image/png','image/webp','image/gif'];

drop policy if exists community_up on storage.objects;
create policy community_up on storage.objects for insert to authenticated
  with check (bucket_id = 'community' and (storage.foldername(name))[1] = auth.uid()::text and public.is_real_user());
drop policy if exists community_read on storage.objects;
create policy community_read on storage.objects for select
  using (bucket_id = 'community' and ((storage.foldername(name))[1] = auth.uid()::text or public.is_admin()
         or exists (select 1 from public.posts p where p.file_path = name and p.status = 'approved')));
drop policy if exists community_del on storage.objects;
create policy community_del on storage.objects for delete to authenticated
  using (bucket_id = 'community' and ((storage.foldername(name))[1] = auth.uid()::text or public.is_admin()));

-- ---------- make the site owner the admin (Google account) ----------
-- insert into public.admins (user_id) select id from auth.users where email = '<owner email>' on conflict do nothing;
