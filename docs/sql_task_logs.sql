SELECT id, task_id, SPLIT_PART(task_name, '.', 5), status, created_at at time zone 'asia/kolkata' as created, updated_at at time zone 'asia/kolkata' as updated, current_timestamp  at time zone 'asia/kolkata'
FROM public.lookup_task
WHERE created_at > '2022-12-05 18:30:00.000000+00' 
ORDER BY created_at DESC
--AND task_name like '%execute_equity_open_interest_task%'

SELECT tl.id, SPLIT_PART(t.task_name, '.', 5) , tl.title, tl.message_type, tl.message, tl.task_id, tl.created_at  at time zone 'asia/kolkata'
FROM public.lookup_tasklog as tl
INNER JOIN public.lookup_task as t
on t."id" = tl."task_id"
WHERE tl.task_id > 821